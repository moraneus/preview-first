import json
import os
import threading
import urllib.error
import urllib.request

import pytest

import serve_preview
from serve_preview import is_stale, make_server, stop, wait_for_selection


class _Srv:
    def __init__(self, dir_, httpd):
        self.dir = dir_
        self.httpd = httpd
        self.url = "http://127.0.0.1:%d" % httpd.server_address[1]


@pytest.fixture
def server(tmp_path):
    (tmp_path / "index.html").write_text("<!DOCTYPE html><title>ok</title>", encoding="utf-8")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "a.css").write_text("body{}", encoding="utf-8")
    httpd = make_server(tmp_path, 0)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    yield _Srv(tmp_path, httpd)
    httpd.shutdown()
    httpd.server_close()


def _get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        return urllib.request.urlopen(req, timeout=5)
    except urllib.error.HTTPError as e:
        return e


def _post(url, obj):
    req = urllib.request.Request(url, data=json.dumps(obj).encode(), headers={"Content-Type": "application/json"}, method="POST")
    try:
        return urllib.request.urlopen(req, timeout=5)
    except urllib.error.HTTPError as e:
        return e


def test_serves_index_and_sets_no_store(server):
    r = _get(server.url + "/index.html")
    assert r.status == 200
    assert r.headers["Cache-Control"] == "no-store"
    assert "text/html" in r.headers["Content-Type"]
    assert _get(server.url + "/assets/a.css").headers["Content-Type"].startswith("text/css")


def test_post_select_writes_file(server):
    r = _post(server.url + "/select", {"direction": "B", "overrides": {"palette": "palette.x"}})
    assert r.status == 204
    data = json.load(open(server.dir / "selection.json", encoding="utf-8"))
    assert data["direction"] == "B" and data["overrides"]["palette"] == "palette.x" and "selected_at" in data


def test_post_invalid_selection_is_400(server):
    assert _post(server.url + "/select", {"nope": 1}).status == 400
    assert _post(server.url + "/other", {"direction": "A"}).status == 404


def test_path_traversal_forbidden(server):
    (server.dir.parent / "secret.txt").write_text("x", encoding="utf-8")
    assert _get(server.url + "/../secret.txt").status == 403
    assert _get(server.url + "/assets/../../secret.txt").status == 403


def test_foreign_host_forbidden(server):
    assert _get(server.url + "/index.html", headers={"Host": "evil.example"}).status == 403
    assert _get(server.url + "/index.html", headers={"Host": "localhost:1"}).status == 200


def test_stale_server_json_detected(tmp_path):
    (tmp_path / "server.json").write_text(json.dumps({"pid": 999999, "port": 1}), encoding="utf-8")
    assert is_stale(tmp_path) is True
    assert is_stale(tmp_path / "nowhere") is False


def test_stop_refuses_unrelated_pid(tmp_path, monkeypatch):
    (tmp_path / "server.json").write_text(json.dumps({"pid": os.getpid(), "port": 1}), encoding="utf-8")
    monkeypatch.setattr(serve_preview, "_cmdline", lambda pid: "python other.py")
    assert stop(tmp_path) is False
    assert not (tmp_path / "server.json").exists()


def test_wait_for_selection(tmp_path):
    assert wait_for_selection(tmp_path, 0.2) is None
    (tmp_path / "selection.json").write_text(json.dumps({"direction": "A"}), encoding="utf-8")
    assert wait_for_selection(tmp_path, 0.2)["direction"] == "A"


def test_status_cli(tmp_path, capsys):
    assert serve_preview.main(["--dir", str(tmp_path), "--status"]) == 0
    assert json.loads(capsys.readouterr().out)["running"] is False


def test_select_requires_json_content_type(server):
    req = urllib.request.Request(server.url + "/select", data=b'{"direction":"A"}', headers={"Content-Type": "text/plain"}, method="POST")
    try:
        r = urllib.request.urlopen(req, timeout=5)
    except urllib.error.HTTPError as e:
        r = e
    assert r.status == 415
    assert not (server.dir / "selection.json").exists()


def test_select_refuses_foreign_origin(server):
    req = urllib.request.Request(server.url + "/select", data=b'{"direction":"A"}',
                                 headers={"Content-Type": "application/json", "Origin": "https://evil.example"}, method="POST")
    try:
        r = urllib.request.urlopen(req, timeout=5)
    except urllib.error.HTTPError as e:
        r = e
    assert r.status == 403
    req = urllib.request.Request(server.url + "/select", data=b'{"direction":"A"}',
                                 headers={"Content-Type": "application/json", "Origin": server.url}, method="POST")
    assert urllib.request.urlopen(req, timeout=5).status == 204


def test_ping_returns_token_and_alive_check(tmp_path):
    from serve_preview import is_alive_server, PING_PATH
    (tmp_path / "index.html").write_text("x", encoding="utf-8")
    httpd = make_server(tmp_path, 0, token="abc123")
    t = threading.Thread(target=httpd.serve_forever, daemon=True); t.start()
    try:
        port = httpd.server_address[1]
        r = urllib.request.urlopen("http://127.0.0.1:%d%s" % (port, PING_PATH), timeout=5)
        assert json.load(r)["token"] == "abc123"
        assert is_alive_server({"port": port, "token": "abc123", "dir": str(tmp_path.resolve())}) is True
        assert is_alive_server({"port": port, "token": "wrong", "dir": str(tmp_path.resolve())}) is False
        (tmp_path / "server.json").write_text(json.dumps({"pid": 4242, "port": port, "token": "abc123", "dir": str(tmp_path.resolve())}), encoding="utf-8")
        assert is_stale(tmp_path) is False
        killed = []
        serve_preview.os.kill = lambda pid, sig: killed.append(pid)  # restored below
        try:
            assert stop(tmp_path) is True and killed == [4242]
        finally:
            del serve_preview.os.kill
    finally:
        httpd.shutdown(); httpd.server_close()


def test_select_rejects_unknown_direction(server):
    (server.dir / "data.json").write_text(json.dumps({"directions": [{"id": "A"}, {"id": "B"}]}), encoding="utf-8")
    assert _post(server.url + "/select", {"direction": "Z", "overrides": {}}).status == 400
    assert _post(server.url + "/select", {"direction": "A", "overrides": {}}).status == 204


def test_watch_directory_shuts_server_down(tmp_path):
    from serve_preview import _watch_directory
    d = tmp_path / "proj"; d.mkdir()
    events = []

    class Fake:
        def shutdown(self):
            events.append("shutdown")

    import shutil
    shutil.rmtree(d)
    _watch_directory(d, Fake(), interval=0.01, max_checks=3)
    assert events == ["shutdown"]


def test_shuffle_endpoint_adds_a_direction(tmp_path):
    import json as _json
    import urllib.request
    from build_preview import build
    from _common import load_devices, load_graph
    from quick_start import author_directions
    from serve_preview import make_server
    from conftest import FIXTURES
    import threading
    graph = load_graph()
    brief = _json.load(open(FIXTURES / "brief_saas.json", encoding="utf-8"))
    d = author_directions(brief, graph, 3)
    (tmp_path / "directions.json").write_text(_json.dumps(d), encoding="utf-8")
    build(d, tmp_path, graph, load_devices())
    httpd = make_server(tmp_path, 0, "tok")
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True); t.start()
    try:
        req = urllib.request.Request("http://127.0.0.1:%d/shuffle" % port, data=b"{}", method="POST",
                                     headers={"Content-Type": "application/json", "Host": "127.0.0.1:%d" % port, "Origin": "http://127.0.0.1:%d" % port})
        body = _json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8"))
        assert body["id"] == "R4" and (tmp_path / "R4" / "draft.html").exists()
        assert len(_json.load(open(tmp_path / "directions.json", encoding="utf-8"))["directions"]) == 4
    finally:
        httpd.shutdown(); httpd.server_close()
