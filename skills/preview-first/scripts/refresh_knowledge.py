"""Refresh live knowledge (font popularity, Baseline status, library releases, design feeds).

Usage: refresh_knowledge.py [--out DIR] [--sources PATH] [--bundled]
Writes fonts.json, features.json, releases.json and feeds.json with a `fetched` timestamp.
Default output is the user cache (~/.cache/preview-first/live); --bundled writes into the skill's
knowledge/live/ (used by the weekly workflow). One failing source never aborts the run.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _common  # noqa: E402

BUNDLED_LIVE = _common.KNOWLEDGE_DIR / "live"
USER_AGENT = "preview-first/%s (+https://github.com/moraneus/preview-first)" % _common.VERSION
BASELINE_MAP = {"high": "widely", "low": "newly", False: "limited", None: "limited"}


# ---------------------------------------------------------------- fetch

def fetch(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


# ---------------------------------------------------------------- parsers (pure)

def parse_google_fonts_metadata(text: str) -> dict:
    body = text.lstrip()
    if body.startswith(")]}'"):
        body = body.split("\n", 1)[1] if "\n" in body else ""
    data = json.loads(body)
    fams = []
    for f in data.get("familyMetadataList", []):
        fams.append({
            "family": f.get("family"),
            "category": f.get("category"),
            "popularity": f.get("popularity"),
            "trending": f.get("trending"),
            "last_modified": f.get("lastModified"),
            "weights": sorted(f.get("fonts", {}).keys()),
        })
    return {"fetched": _common.now_iso(), "source": "https://fonts.google.com/metadata/fonts", "families": fams}


def parse_web_features(text: str, ids: Sequence[str]) -> dict:
    data = json.loads(text)
    feats = data.get("features", data)
    out = {}
    for fid in ids:
        f = feats.get(fid)
        if not f:
            continue
        status = f.get("status", {})
        out[fid] = {
            "name": f.get("name"),
            "baseline": BASELINE_MAP.get(status.get("baseline"), "limited"),
            "baseline_low_date": status.get("baseline_low_date"),
            "baseline_high_date": status.get("baseline_high_date"),
            "support": status.get("support", {}),
        }
    return {"fetched": _common.now_iso(), "source": "web-features", "features": out}


def _text(el, *names) -> str:
    for n in names:
        found = el.find(n)
        if found is not None and (found.text or "").strip():
            return found.text.strip()
    return ""


def _safe_xml(text: str):
    """Parse XML with the standard library but refuse DTDs, which closes the XXE and
    entity-expansion routes without a third-party parser."""
    head = text[:4096].lower()
    if "<!doctype" in head or "<!entity" in text.lower():
        raise ValueError("XML with a DTD is not accepted")
    return ET.fromstring(text)


def parse_atom(text: str) -> List[dict]:
    root = _safe_xml(text)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    entries = []
    for e in root.findall("a:entry", ns):
        link = ""
        for l in e.findall("a:link", ns):
            if l.get("rel", "alternate") == "alternate":
                link = l.get("href", "")
                break
        entries.append({"title": _text(e, "a:title".replace("a:", "{http://www.w3.org/2005/Atom}")), "link": link,
                        "updated": _text(e, "{http://www.w3.org/2005/Atom}updated", "{http://www.w3.org/2005/Atom}published")})
    return entries


def parse_rss(text: str) -> List[dict]:
    root = _safe_xml(text)
    if root.tag.endswith("feed"):
        return parse_atom(text)
    items = []
    for it in root.iter("item"):
        items.append({"title": _text(it, "title"), "link": _text(it, "link"), "updated": _text(it, "pubDate", "{http://purl.org/dc/elements/1.1/}date")})
    return items


def parse_npm_point(text: str) -> dict:
    data = json.loads(text)
    return {"downloads": int(data.get("downloads", 0)), "start": data.get("start"), "end": data.get("end")}


# ---------------------------------------------------------------- refresh

def trim_fonts(fonts: dict, keep: Sequence[str] = (), popularity_limit: int = 400, trending_limit: int = 100) -> dict:
    """Keep the snapshot small: popular or trending families plus any the graph references."""
    keep_set = set(keep)
    fams = [f for f in fonts.get("families", [])
            if f["family"] in keep_set
            or (f.get("popularity") or 10**6) <= popularity_limit
            or (f.get("trending") or 10**6) <= trending_limit]
    out = dict(fonts)
    out["families"] = fams
    out["total_families"] = len(fonts.get("families", []))
    return out


def graph_font_families(graph: Optional[dict] = None) -> List[str]:
    try:
        graph = graph or _common.load_graph()
    except (OSError, ValueError):
        return []
    fams = []
    for n in graph.get("nodes", []):
        if n.get("kind") == "type-pairing":
            for face in ("heading", "body", "mono"):
                fam = (n.get(face) or {}).get("family")
                if fam:
                    fams.append(fam)
    return fams


def refresh(sources: dict, out_dir: Path, fetcher: Callable[..., str] = fetch, limit: int = 15, keep_families: Optional[Sequence[str]] = None) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {"ok": [], "failed": [], "skipped": [], "out_dir": str(out_dir)}
    keep_families = graph_font_families() if keep_families is None else keep_families

    def attempt(name: str, fn):
        try:
            result = fn()
            report["ok"].append(name)
            return result
        except Exception as exc:  # noqa: BLE001 - every source failure is recorded, not raised
            report["failed"].append({"name": name, "error": "%s: %s" % (type(exc).__name__, exc)})
            return None

    fonts_src = sources.get("fonts")
    if fonts_src:
        fonts = attempt("fonts", lambda: trim_fonts(parse_google_fonts_metadata(fetcher(fonts_src["url"])), keep_families))
        if fonts:
            _common.dump_json(out_dir / "fonts.json", fonts)

    feat_src = sources.get("features")
    if feat_src:
        feats = attempt("features", lambda: parse_web_features(fetcher(feat_src["url"], 60), feat_src.get("ids", [])))
        if feats:
            _common.dump_json(out_dir / "features.json", feats)

    releases: Dict[str, dict] = {}
    npm_url = sources.get("npm_url", "https://api.npmjs.org/downloads/point/last-week/{name}")
    for rel in sources.get("releases", []):
        entries = attempt("release:%s" % rel["name"], lambda rel=rel: parse_atom(fetcher(rel["url"])))
        if entries is not None:
            releases[rel["name"]] = {"url": rel["url"], "latest": entries[0] if entries else None, "recent": entries[:5]}
    for pkg in sources.get("npm", []):
        name = pkg["name"]
        point = attempt("npm:%s" % name, lambda name=name: parse_npm_point(fetcher(npm_url.format(name=name))))
        if point:
            key = next((r for r in releases if (sources_npm_name(sources, r) or r) == name), None)
            if key:
                releases[key]["npm_weekly_downloads"] = point["downloads"]
            releases.setdefault("_npm", {})[name] = point["downloads"]
    if releases:
        _common.dump_json(out_dir / "releases.json", {"fetched": _common.now_iso(), "releases": releases})

    feeds: Dict[str, dict] = {}
    for feed in sources.get("feeds", []):
        name = "feed:%s" % feed["name"]
        if feed.get("verify"):
            report["skipped"].append({"name": name, "error": "marked verify: URL not yet confirmed"})
            continue
        items = attempt(name, lambda feed=feed: parse_rss(fetcher(feed["url"])))
        if items is not None:
            feeds[feed["name"]] = {"url": feed["url"], "items": items[:limit]}
    if feeds:
        _common.dump_json(out_dir / "feeds.json", {"fetched": _common.now_iso(), "feeds": feeds})
    return report


def sources_npm_name(sources: dict, release_name: str) -> Optional[str]:
    for rel in sources.get("releases", []):
        if rel["name"] == release_name:
            return rel.get("npm")
    return None


# ---------------------------------------------------------------- reading live data

def _fetched_at(directory: Path) -> Optional[_dt.datetime]:
    latest = None
    for f in Path(directory).glob("*.json"):
        try:
            stamp = _common.load_json(f).get("fetched")
        except (OSError, ValueError, AttributeError):
            continue
        if not stamp:
            continue
        try:
            dt = _dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        except ValueError:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=_dt.timezone.utc)
        latest = dt if latest is None or dt > latest else latest
    return latest


def newest_live_dir(bundled: Path = BUNDLED_LIVE, cache: Optional[Path] = None) -> Path:
    cache = cache if cache is not None else _common.cache_dir() / "live"
    b, c = _fetched_at(bundled) if Path(bundled).exists() else None, _fetched_at(cache) if Path(cache).exists() else None
    if c and (not b or c > b):
        return Path(cache)
    return Path(bundled)


def is_stale(directory: Path, days: int = 7) -> bool:
    at = _fetched_at(directory)
    if at is None:
        return True
    return (_dt.datetime.now(_dt.timezone.utc) - at).days >= days


def load_live(directory: Optional[Path] = None) -> dict:
    directory = Path(directory) if directory else newest_live_dir()
    out = {}
    for name in ("fonts", "features", "releases", "feeds"):
        f = directory / (name + ".json")
        if f.exists():
            try:
                out[name] = _common.load_json(f)
            except ValueError:
                pass
    return out


def annotate_graph(graph: dict, live: dict) -> dict:
    """Return a deep copy of the graph with `live` fields on type pairings and platform features."""
    out = json.loads(json.dumps(graph))
    fams = {f["family"]: f for f in (live.get("fonts") or {}).get("families", [])}
    feats = (live.get("features") or {}).get("features", {})
    for n in out["nodes"]:
        if n["kind"] == "type-pairing":
            h = fams.get((n.get("heading") or {}).get("family"))
            b = fams.get((n.get("body") or {}).get("family"))
            ranks = [x["popularity"] for x in (h, b) if x and x.get("popularity")]
            trend = [x["trending"] for x in (h, b) if x and x.get("trending")]
            if ranks or trend:
                n["live"] = {
                    "popularity_rank": min(ranks) if ranks else None,
                    "trending": bool(trend and min(trend) <= 25),
                    "as_of": (live.get("fonts") or {}).get("fetched"),
                }
        elif n["kind"] == "platform-feature":
            f = feats.get(n.get("web_features_id") or n["id"].split(".", 1)[1])
            if f:
                n["live"] = {"baseline": f["baseline"], "support": f.get("support", {}), "as_of": (live.get("features") or {}).get("fetched")}
    return out


# ---------------------------------------------------------------- CLI

def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Refresh preview-first live knowledge from machine-readable sources.")
    ap.add_argument("--sources", default=str(_common.KNOWLEDGE_DIR / "sources.json"))
    ap.add_argument("--out", help="output directory (default: user cache)")
    ap.add_argument("--bundled", action="store_true", help="write into the skill's knowledge/live/")
    ap.add_argument("--status", action="store_true", help="report where live data is and whether it is stale")
    ns = ap.parse_args(list(argv))
    if ns.status:
        d = newest_live_dir()
        print(json.dumps({"dir": str(d), "fetched": (_fetched_at(d).isoformat() if _fetched_at(d) else None), "stale": is_stale(d)}))
        return 0
    out_dir = Path(ns.out) if ns.out else (BUNDLED_LIVE if ns.bundled else _common.cache_dir() / "live")
    report = refresh(_common.load_json(ns.sources), out_dir)
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
