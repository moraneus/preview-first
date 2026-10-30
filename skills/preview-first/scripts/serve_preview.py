"""Serve .design-preview/ on localhost and record the developer's selection.

Usage:
  serve_preview.py --dir .design-preview [--port N] [--open]      start detached, print {"url": ...}
  serve_preview.py --dir .design-preview --wait 1800              block until selection.json exists
  serve_preview.py --dir .design-preview --stop | --status
  serve_preview.py --dir DIR --port N --foreground                 (used by the detached child)

Only localhost Host headers are accepted; paths may not escape the directory; POST /select writes
selection.json after validating it against the schema. Nothing else is written.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import webbrowser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _common  # noqa: E402
from validate_graph import validate_file  # noqa: E402

LOCAL_HOSTS = {"localhost", "127.0.0.1", "[::1]", "::1"}


# ---------------------------------------------------------------- handler

class PreviewHandler(SimpleHTTPRequestHandler):
    preview_dir: Path = Path(".")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(self.preview_dir), **kwargs)

    def log_message(self, fmt, *args):  # quiet
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def _guard(self) -> bool:
        host = (self.headers.get("Host") or "").strip()
        bare = host.rsplit(":", 1)[0] if host.count(":") == 1 or host.startswith("[") else host
        if bare.startswith("[") and "]" in bare:
            bare = bare[: bare.index("]") + 1]
        if bare not in LOCAL_HOSTS:
            self.send_error(HTTPStatus.FORBIDDEN, "preview is local only")
            return False
        raw = self.path.split("?", 1)[0]
        if ".." in raw.split("/"):
            self.send_error(HTTPStatus.FORBIDDEN, "path escapes the preview directory")
            return False
        return True

    def do_GET(self):
        if self._guard():
            super().do_GET()

    def do_HEAD(self):
        if self._guard():
            super().do_HEAD()

    def do_POST(self):
        if not self._guard():
            return
        if self.path.split("?", 1)[0] != "/select":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except (ValueError, UnicodeDecodeError):
            self.send_error(HTTPStatus.BAD_REQUEST, "body must be JSON")
            return
        problems = validate_file(body, "selection", _common.load_schema())
        if problems:
            self.send_error(HTTPStatus.BAD_REQUEST, "; ".join(problems[:3]))
            return
        body.setdefault("overrides", {})
        body.setdefault("selected_at", _common.now_iso())
        _common.dump_json(Path(self.directory) / "selection.json", body)
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()


def make_server(directory: Path, port: int = 0) -> ThreadingHTTPServer:
    handler = type("BoundPreviewHandler", (PreviewHandler,), {"preview_dir": Path(directory)})
    httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
    httpd.daemon_threads = True
    return httpd


# ---------------------------------------------------------------- process helpers

def _server_json(directory: Path) -> Path:
    return Path(directory) / "server.json"


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _cmdline(pid: int) -> str:
    try:
        if sys.platform == "win32":
            out = subprocess.run(["wmic", "process", "where", "ProcessId=%d" % pid, "get", "CommandLine"],
                                 capture_output=True, text=True, timeout=5).stdout
        else:
            out = subprocess.run(["ps", "-o", "command=", "-p", str(pid)], capture_output=True, text=True, timeout=5).stdout
        return out.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def read_status(directory: Path) -> Optional[dict]:
    p = _server_json(directory)
    if not p.exists():
        return None
    try:
        return _common.load_json(p)
    except (OSError, ValueError):
        return None


def is_stale(directory: Path) -> bool:
    info = read_status(directory)
    if not info:
        return False
    pid = int(info.get("pid", 0) or 0)
    if not pid or not _alive(pid):
        return True
    return "serve_preview" not in _cmdline(pid)


def stop(directory: Path) -> bool:
    info = read_status(directory)
    stopped = False
    if info:
        pid = int(info.get("pid", 0) or 0)
        if pid and _alive(pid):
            cmd = _cmdline(pid)
            if "serve_preview" in cmd and str(Path(directory).resolve()) in cmd or ("serve_preview" in cmd and str(directory) in cmd):
                try:
                    os.kill(pid, signal.SIGTERM)
                    stopped = True
                except OSError:
                    stopped = False
    try:
        _server_json(directory).unlink()
    except FileNotFoundError:
        pass
    return stopped


def wait_for_selection(directory: Path, timeout_s: float) -> Optional[dict]:
    deadline = time.time() + timeout_s
    target = Path(directory) / "selection.json"
    while True:
        if target.exists():
            try:
                return _common.load_json(target)
            except ValueError:
                pass
        if time.time() >= deadline:
            return None
        time.sleep(0.25)


# ---------------------------------------------------------------- start

def serve_foreground(directory: Path, port: int, open_browser: bool = False) -> int:
    directory = Path(directory).resolve()
    httpd = make_server(directory, port)
    actual = httpd.server_address[1]
    url = "http://127.0.0.1:%d/index.html" % actual
    _common.dump_json(_server_json(directory), {"port": actual, "pid": os.getpid(), "url": url, "dir": str(directory), "started": _common.now_iso()})
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    def _term(signum, frame):
        raise KeyboardInterrupt

    try:
        signal.signal(signal.SIGTERM, _term)
    except (ValueError, OSError):
        pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        try:
            _server_json(directory).unlink()
        except FileNotFoundError:
            pass
    return 0


def start_detached(directory: Path, port: int, open_browser: bool) -> dict:
    directory = Path(directory).resolve()
    if is_stale(directory):
        _server_json(directory).unlink(missing_ok=True)
    info = read_status(directory)
    if info and _alive(int(info.get("pid", 0) or 0)):
        if open_browser:
            webbrowser.open(info["url"])
        return info
    args = [sys.executable, str(Path(__file__).resolve()), "--dir", str(directory), "--port", str(port), "--foreground"]
    if open_browser:
        args.append("--open")
    kwargs = dict(stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=str(directory))
    if sys.platform == "win32":
        kwargs["creationflags"] = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(args, **kwargs)
    for _ in range(100):
        info = read_status(directory)
        if info and info.get("port"):
            return info
        time.sleep(0.05)
    raise RuntimeError("preview server did not start")


# ---------------------------------------------------------------- CLI

def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Serve the preview-first browser preview on localhost.")
    ap.add_argument("--dir", default=".design-preview")
    ap.add_argument("--port", type=int, default=0)
    ap.add_argument("--open", action="store_true", help="open the browser")
    ap.add_argument("--wait", type=float, metavar="SECONDS", help="block until selection.json exists")
    ap.add_argument("--stop", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--foreground", action="store_true", help=argparse.SUPPRESS)
    ns = ap.parse_args(list(argv))
    directory = Path(ns.dir)

    if ns.stop:
        print(json.dumps({"stopped": stop(directory)}))
        return 0
    if ns.status:
        info = read_status(directory)
        running = bool(info) and not is_stale(directory)
        print(json.dumps({"running": running, "server": info if running else None}))
        return 0
    if ns.foreground:
        return serve_foreground(directory, ns.port, ns.open)
    if ns.wait is not None and read_status(directory) and not is_stale(directory):
        sel = wait_for_selection(directory, ns.wait)
        print(json.dumps({"selection": sel}))
        return 0 if sel else 2
    if not (directory / "index.html").exists():
        print("no preview found at %s; run build_preview.py first" % directory, file=sys.stderr)
        return 1
    info = start_detached(directory, ns.port, ns.open)
    if ns.wait is not None:
        sel = wait_for_selection(directory, ns.wait)
        print(json.dumps({"url": info["url"], "selection": sel}))
        return 0 if sel else 2
    print(json.dumps({"url": info["url"], "pid": info["pid"], "port": info["port"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
