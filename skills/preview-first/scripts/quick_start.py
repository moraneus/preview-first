"""One command from brief to open preview: recommend, author directions with honest default copy,
build, serve, print the URL. Claude can refine names, rationale and copy afterwards and rebuild.

Usage: quick_start.py --brief .design-preview/brief.json [--count 4] [--dir .design-preview] [--open] [--no-serve]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _common  # noqa: E402
from build_preview import build  # noqa: E402
from recommend import normalise_brief, recommend  # noqa: E402

IDS = "ABCDEFGH"


def author_directions(brief: dict, graph: dict, count: int, copy: dict = None) -> dict:
    """directions.json with one direction per bundle: the style's name, its summary as the rationale,
    and the copy Claude wrote (or copy derived from the brief by the draft engine, no invented claims)."""
    idx = _common.node_index(graph)
    bundles = recommend(brief, graph, max(3, min(8, count)))
    dirs = []
    for i, b in enumerate(bundles):
        style = idx[b["style"]]
        d = {"id": IDS[i], "name": style["name"], "rationale": style.get("summary", ""), "bundle": b}
        if copy:
            d["copy"] = dict(copy)
        dirs.append(d)
    return {"version": 1, "brief": normalise_brief(brief, graph), "directions": dirs}


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Brief to open preview in one step.")
    ap.add_argument("--brief", required=True)
    ap.add_argument("--count", type=int, default=4)
    ap.add_argument("--copy", help="copy.json written by Claude from the brief (headline, subhead, nav, features, calls to action)")
    ap.add_argument("--dir", default=".design-preview")
    ap.add_argument("--graph", default=str(_common.KNOWLEDGE_DIR / "graph.json"))
    ap.add_argument("--open", action="store_true")
    ap.add_argument("--no-serve", action="store_true")
    ns = ap.parse_args(list(argv))
    graph = _common.load_json(ns.graph)
    try:
        from refresh_knowledge import annotate_graph, load_live
        live = load_live()
        if live:
            graph = annotate_graph(graph, live)
    except Exception:
        pass
    brief = _common.load_json(ns.brief)
    out = Path(ns.dir)
    copy = _common.load_json(ns.copy) if ns.copy else None
    directions = author_directions(brief, graph, ns.count, copy)
    _common.dump_json(out / "directions.json", directions)
    report = build(directions, out, graph, _common.load_json(_common.KNOWLEDGE_DIR / "devices.json")["devices"])
    result = {"directions": [(d["id"], d["name"]) for d in directions["directions"]], "pages": len(report["pages"]), "warnings": report["warnings"]}
    if not ns.no_serve:
        from serve_preview import start_detached
        info = start_detached(out, 0, ns.open)
        result["url"] = info.get("url")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
