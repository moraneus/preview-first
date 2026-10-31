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
import secrets
import signal
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _common  # noqa: E402
from validate_graph import validate_file  # noqa: E402

LOCAL_HOSTS = {"localhost", "127.0.0.1", "[::1]", "::1"}
PING_PATH = "/__pf/ping"
_SHUFFLE_LOCK = threading.Lock()
MAX_BODY = 64 * 1024


# ---------------------------------------------------------------- handler

class PreviewHandler(SimpleHTTPRequestHandler):
    preview_dir: Path = Path(".")
    token: str = ""

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
        if not self._guard():
            return
        if self.path.split("?", 1)[0] == PING_PATH:
            body = json.dumps({"token": self.token, "dir": str(Path(self.directory).resolve()), "pid": os.getpid()}).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def do_HEAD(self):
        if self._guard():
            super().do_HEAD()

    def do_POST(self):
        if not self._guard():
            return
        route = self.path.split("?", 1)[0]
        if route not in ("/select", "/shuffle", "/more"):
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        # Cross-site protection: a foreign page cannot send application/json without a CORS
        # preflight (never approved here), and any Origin that is not local is refused outright.
        ctype = (self.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        if ctype != "application/json":
            self.send_error(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "send application/json")
            return
        origin = (self.headers.get("Origin") or "").strip()
        if origin and origin != "null":
            host = origin.split("://", 1)[-1].split("/", 1)[0]
            bare = host.rsplit(":", 1)[0] if host.count(":") == 1 else host
            if bare not in LOCAL_HOSTS:
                self.send_error(HTTPStatus.FORBIDDEN, "cross-origin selection refused")
                return
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_BODY:
                self.send_error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
                return
            body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except (ValueError, UnicodeDecodeError):
            self.send_error(HTTPStatus.BAD_REQUEST, "body must be JSON")
            return
        if route in ("/shuffle", "/more"):
            self._shuffle(body if route == "/more" else {})
            return
        problems = validate_file(body, "selection", _common.load_schema())
        if problems:
            self.send_error(HTTPStatus.BAD_REQUEST, "; ".join(problems[:3]))
            return
        known = _known_directions(Path(self.directory))
        if known is not None and body.get("direction") not in known:
            self.send_error(HTTPStatus.BAD_REQUEST, "unknown direction %r" % body.get("direction"))
            return
        body.setdefault("overrides", {})
        body.setdefault("selected_at", _common.now_iso())
        _common.dump_json(Path(self.directory) / "selection.json", body)
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def _shuffle(self, body: dict = None):
        directory = Path(self.directory)
        if not (directory / "directions.json").exists():
            self.send_error(HTTPStatus.BAD_REQUEST, "no directions.json beside the preview")
            return
        try:
            with _SHUFFLE_LOCK:
                result = _shuffle_impl(directory, body if isinstance(body, dict) else {})
        except Exception as exc:  # the page shows the message; nothing else to do
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc)[:200])
            return
        payload = json.dumps(result).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def _shuffle_impl(directory: Path, body: dict = None) -> dict:
    """Append directions to directions.json beside the preview and rebuild in place.
    body.mode: "random" (default), "like" with body.direction, or "all"."""
    import random
    from build_preview import build
    from random_direction import all_styles, random_direction, variation_of
    body = body or {}
    directions_path = directory / "directions.json"
    directions = _common.load_json(directions_path)
    graph = _common.load_graph()
    mode = body.get("mode", "random")
    if mode == "all":
        added = all_styles(directions, graph)
    elif mode == "like":
        known = {d["id"] for d in directions["directions"]}
        if body.get("direction") not in known:
            raise ValueError("unknown direction")
        added = []
        rng = random.Random()
        for _ in range(5):
            added.append(variation_of({"brief": directions["brief"], "directions": directions["directions"] + added}, graph, body["direction"], rng))
    else:
        added = [random_direction(directions, graph, random.Random())]
    if not added:
        return {"id": None, "name": None, "added": []}
    directions["directions"].extend(added)
    _common.dump_json(directions_path, directions)
    build(directions, directory, graph, _common.load_devices())
    return {"id": added[0]["id"], "name": added[0]["name"], "added": [d["id"] for d in added]}


def _known_directions(directory: Path):
    data = directory / "data.json"
    if not data.exists():
        return None
    try:
        return {d["id"] for d in _common.load_json(data).get("directions", [])}
    except (OSError, ValueError, KeyError, TypeError):
        return None


def make_server(directory: Path, port: int = 0, token: Optional[str] = None) -> ThreadingHTTPServer:
    handler = type("BoundPreviewHandler", (PreviewHandler,), {"preview_dir": Path(directory), "token": token or secrets.token_hex(16)})
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


def is_alive_server(info: dict, timeout: float = 1.0) -> bool:
    """True when a preview server answers the ping on the recorded port with the recorded token
    for the recorded directory. This is what makes stop() safe: it never trusts a pid alone."""
    try:
        port = int(info.get("port") or 0)
        if not port:
            return False
        req = urllib.request.Request("http://127.0.0.1:%d%s" % (port, PING_PATH), headers={"Host": "127.0.0.1:%d" % port})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return False
    if data.get("token") != info.get("token"):
        return False
    want = info.get("dir")
    return not want or str(Path(want).resolve()) == str(Path(data.get("dir", "")).resolve())


def is_stale(directory: Path) -> bool:
    info = read_status(directory)
    if not info:
        return False
    return not is_alive_server(info)


def stop(directory: Path) -> bool:
    info = read_status(directory)
    stopped = False
    if info and is_alive_server(info):
        pid = int(info.get("pid", 0) or 0)
        if pid:
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

def _watch_directory(directory: Path, httpd, interval: float = 2.0, max_checks: Optional[int] = None) -> None:
    """Shut the server down once the project directory disappears."""
    checks = 0
    while max_checks is None or checks < max_checks:
        checks += 1
        if not Path(directory).exists():
            httpd.shutdown()
            return
        time.sleep(interval)


def serve_foreground(directory: Path, port: int, open_browser: bool = False) -> int:
    directory = Path(directory).resolve()
    token = secrets.token_hex(16)
    httpd = make_server(directory, port, token)
    actual = httpd.server_address[1]
    url = "http://127.0.0.1:%d/index.html" % actual
    _common.dump_json(_server_json(directory), {"port": actual, "pid": os.getpid(), "url": url, "dir": str(directory), "token": token, "started": _common.now_iso()})
    threading.Thread(target=_watch_directory, args=(directory, httpd), daemon=True).start()
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
        try:
            _server_json(directory).unlink()
        except FileNotFoundError:
            pass
    info = read_status(directory)
    if info and is_alive_server(info):
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
