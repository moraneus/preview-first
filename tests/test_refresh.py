import json
import time

import pytest

from conftest import FIXTURES, ROOT
from refresh_knowledge import (
    annotate_graph,
    is_stale,
    newest_live_dir,
    parse_atom,
    parse_google_fonts_metadata,
    parse_npm_point,
    parse_rss,
    parse_web_features,
    refresh,
)


def test_parse_google_fonts_metadata():
    out = parse_google_fonts_metadata((FIXTURES / "google_fonts_metadata.txt").read_text(encoding="utf-8"))
    fams = {f["family"]: f for f in out["families"]}
    assert fams["Figtree"]["popularity"] == 25 and fams["Figtree"]["trending"] == 3 and fams["Figtree"]["category"] == "Sans Serif"
    assert out["fetched"]


def test_parse_web_features():
    out = parse_web_features((FIXTURES / "web_features.json").read_text(encoding="utf-8"), ["container-queries", "anchor-positioning", "light-dark", "missing"])
    f = out["features"]
    assert f["container-queries"]["baseline"] == "widely" and f["light-dark"]["baseline"] == "newly" and f["anchor-positioning"]["baseline"] == "limited"
    assert f["container-queries"]["support"]["chrome"] == "106"
    assert "missing" not in f


def test_parse_atom_and_rss():
    entries = parse_atom((FIXTURES / "releases.atom").read_text(encoding="utf-8"))
    assert entries[0]["title"] == "v12.30.0" and entries[0]["link"].startswith("https://github.com/") and entries[0]["updated"].startswith("2026-10-20")
    items = parse_rss((FIXTURES / "feed.xml").read_text(encoding="utf-8"))
    assert items[0]["title"].startswith("Baseline 2026") and items[0]["link"] == "https://web.dev/blog/baseline-2026" and items[0]["updated"]


def test_parse_npm_point():
    assert parse_npm_point('{"downloads": 12345, "start": "2026-10-20", "end": "2026-10-26", "package": "motion"}')["downloads"] == 12345


def test_refresh_records_failures_and_writes_others(tmp_path):
    sources = {
        "fonts": {"url": "https://fonts.example/metadata", "parser": "google_fonts_metadata"},
        "features": {"url": "https://features.example/data.json", "parser": "web_features", "ids": ["container-queries"]},
        "releases": [{"name": "motion", "url": "https://github.example/releases.atom"}, {"name": "broken", "url": "https://broken.example/x.atom"}],
        "npm": [{"name": "motion"}],
        "feeds": [{"name": "web.dev", "url": "https://feed.example/feed.xml"}, {"name": "skip", "url": "https://x", "verify": True}],
    }

    def fetcher(url, timeout=15):
        if "broken" in url:
            raise OSError("boom")
        if "metadata" in url:
            return (FIXTURES / "google_fonts_metadata.txt").read_text(encoding="utf-8")
        if "data.json" in url:
            return (FIXTURES / "web_features.json").read_text(encoding="utf-8")
        if "releases.atom" in url:
            return (FIXTURES / "releases.atom").read_text(encoding="utf-8")
        if "npmjs" in url:
            return '{"downloads": 7}'
        return (FIXTURES / "feed.xml").read_text(encoding="utf-8")

    report = refresh(sources, tmp_path, fetcher=fetcher)
    assert "fonts" in report["ok"] and "features" in report["ok"] and "release:motion" in report["ok"] and "feed:web.dev" in report["ok"]
    assert any(f["name"] == "release:broken" for f in report["failed"])
    assert any(f["name"] == "feed:skip" and "verify" in f["error"] for f in report["skipped"])
    for name in ("fonts.json", "features.json", "releases.json", "feeds.json"):
        assert (tmp_path / name).exists(), name
    rel = json.load(open(tmp_path / "releases.json", encoding="utf-8"))
    assert rel["releases"]["motion"]["latest"]["title"] == "v12.30.0" and rel["releases"]["motion"]["npm_weekly_downloads"] == 7


def test_annotate_graph_adds_live_fields(tmp_path):
    graph = {"nodes": [
        {"id": "type-pairing.x", "kind": "type-pairing", "name": "x", "heading": {"family": "Fraunces"}, "body": {"family": "Figtree"}},
        {"id": "platform-feature.container-queries", "kind": "platform-feature", "name": "cq", "baseline": "newly", "web_features_id": "container-queries"},
        {"id": "style.s", "kind": "style", "name": "s"},
    ], "edges": [{"from": "style.s", "to": "platform-feature.container-queries", "kind": "requires", "weight": 1}]}
    live = {
        "fonts": parse_google_fonts_metadata((FIXTURES / "google_fonts_metadata.txt").read_text(encoding="utf-8")),
        "features": parse_web_features((FIXTURES / "web_features.json").read_text(encoding="utf-8"), ["container-queries"]),
    }
    out = annotate_graph(graph, live)
    pairing = next(n for n in out["nodes"] if n["id"] == "type-pairing.x")
    assert pairing["live"]["popularity_rank"] == 25 and pairing["live"]["trending"] is True
    feat = next(n for n in out["nodes"] if n["id"] == "platform-feature.container-queries")
    assert feat["live"]["baseline"] == "widely" and feat["baseline"] == "newly"
    assert graph["nodes"][0].get("live") is None  # original untouched


def test_is_stale_and_newest(tmp_path, monkeypatch):
    bundled = tmp_path / "bundled"
    cache = tmp_path / "cache"
    bundled.mkdir(); cache.mkdir()
    (bundled / "fonts.json").write_text(json.dumps({"fetched": "2020-01-01T00:00:00+00:00"}), encoding="utf-8")
    assert newest_live_dir(bundled, cache) == bundled
    assert is_stale(bundled, days=7) is True
    (cache / "fonts.json").write_text(json.dumps({"fetched": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())}), encoding="utf-8")
    assert newest_live_dir(bundled, cache) == cache
    assert is_stale(cache, days=7) is False


def test_sources_json_shape():
    sources = json.load(open(ROOT / "skills/preview-first/knowledge/sources.json", encoding="utf-8"))
    assert sources["fonts"]["url"].startswith("https://") and sources["features"]["ids"]
    assert len(sources["feeds"]) >= 8 and len(sources["releases"]) >= 5
    assert all(f["url"].startswith("https://") for f in sources["feeds"])


def test_workflows_exist():
    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    refresh_wf = (ROOT / ".github/workflows/refresh.yml").read_text(encoding="utf-8")
    assert "validate_graph.py" in ci and "pytest" in ci and "3.9" in ci
    assert "schedule" in refresh_wf and "refresh_knowledge.py" in refresh_wf and "create-pull-request" in refresh_wf


def test_xml_with_dtd_is_refused():
    evil = '<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "aaaa">]><rss><channel><item><title>&a;</title></item></channel></rss>'
    with pytest.raises(ValueError):
        parse_rss(evil)


def test_trim_fonts_keeps_graph_and_popular():
    from refresh_knowledge import trim_fonts
    fonts = {"families": [{"family": "A", "popularity": 1, "trending": 900}, {"family": "B", "popularity": 900, "trending": 900}, {"family": "C", "popularity": 900, "trending": 5}]}
    out = trim_fonts(fonts, keep=["B"], popularity_limit=10, trending_limit=10)
    assert {f["family"] for f in out["families"]} == {"A", "B", "C"} and out["total_families"] == 3
    assert {f["family"] for f in trim_fonts(fonts, keep=[], popularity_limit=10, trending_limit=10)["families"]} == {"A", "C"}
