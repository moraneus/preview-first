"""Add a randomly composed direction to directions.json: a style not yet in the set, a palette and
pairing that pair with it, a random draw of fitting ideas, and random section variants. Used by the
preview's "Surprise me" button and by Claude when the developer asks for something unexpected.

Usage: random_direction.py --directions PATH [--seed N] [--build OUT]
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _common  # noqa: E402
from recommend import _Graph, _candidates, _idea_scores, resolve_moods, resolve_product_type  # noqa: E402

EXCLUSIVE = ("nav-", "hero-", "features-", "proof-", "cta-", "footer-", "texture-", "app-")


def random_direction(directions: dict, graph: dict, rng: random.Random) -> dict:
    g = _Graph(graph)
    brief = directions.get("brief", {})
    product = resolve_product_type(brief.get("product_type", ""), g)
    moods = resolve_moods(brief.get("moods", []), g)
    page_type = brief.get("page_type", "marketing")
    used_styles = {d["bundle"]["style"] for d in directions["directions"]}
    styles = [s for s in g.by_kind["style"] if s["id"] not in used_styles] or list(g.by_kind["style"])
    style = rng.choice(styles)
    pals = _candidates(g, style["id"], "palette.", moods, (brief.get("constraints") or {}).get("scheme"))
    pairs = _candidates(g, style["id"], "type-pairing.", moods, None)
    pal = rng.choice(pals[:5])[0] if pals else g.by_kind["palette"][0]["id"]
    pair = rng.choice(pairs[:5])[0] if pairs else g.by_kind["type-pairing"][0]["id"]
    treatments = {g.idx[e["to"]]["axis"]: g.idx[e["to"]]["value"] for e in g.edges(style["id"], "defaults_to", "treatment.")}
    level = rng.choice([1, 2, 2, 3])
    motion = sorted(e["to"] for e in g.edges(style["id"], "defaults_to", "motion-pattern.") if g.idx[e["to"]]["level"] <= level)
    icons = g.edges(style["id"], "pairs_with", "icon-set.")
    # ideas: a random draw weighted by fit, one per hook family, 8 to 12 of them
    ranked = _idea_scores(g, style, product, moods, page_type)
    pool = [iid for iid, sc in ranked if sc > 0] or [iid for iid, _ in ranked]
    rng.shuffle(pool)
    chosen, families = [], set()
    for iid in pool:
        hook = g.idx[iid].get("renders") or ""
        fam = hook.split("-", 1)[0] + "-" if hook else ""
        if fam and fam in families and fam in EXCLUSIVE:
            continue
        chosen.append(iid)
        if fam:
            families.add(fam)
        if len(chosen) >= rng.randint(8, 12):
            break
    # random section variants from the page type's vocabulary
    from drafts import VARIANTS  # type: ignore
    layout = {}
    for section, options in VARIANTS.get(page_type, {}).items():
        if section in ("table",):
            continue
        choices = [v for v in options if v not in ("centered", "columns", "bento", "none")] or options
        if rng.random() < 0.7:
            layout[section] = rng.choice(choices)
    n = len(directions["directions"]) + 1
    names = ["Wildcard", "Long shot", "Curveball", "Left field", "Second wind", "Night draw", "Loose cannon", "Sidestep"]
    return {
        "id": "R%d" % n, "name": "%s %d" % (rng.choice(names), n), "rationale": "A random draw: %s with %s and %s. Keep it, reshuffle, or steal one idea from it." % (
            style["name"], g.idx[pal]["name"], g.idx[pair]["name"]),
        "bundle": {"style": style["id"], "style_family": style["family"], "palette": pal, "type_pairing": pair, "treatments": treatments,
                   "motion": motion or ["motion-pattern.none"], "motion_level": level, "icon_set": icons[0]["to"] if icons else "icon-set.lucide",
                   "ideas": chosen, "radius_scale": rng.choice(["none", "sm", "md", "lg", "pill"]) if rng.random() < 0.3 else style["radius_scale"],
                   "density": style["density"], "alternatives": {"palettes": [p[0] for p in pals[:5] if p[0] != pal], "type_pairings": [p[0] for p in pairs[:5] if p[0] != pair], "icon_sets": []}},
        "layout": layout,
        "copy": dict(directions["directions"][0].get("copy") or {}) if directions["directions"] else {},
    }


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Append a random direction.")
    ap.add_argument("--directions", required=True)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--build", help="preview directory to rebuild after adding")
    ap.add_argument("--graph", default=str(_common.KNOWLEDGE_DIR / "graph.json"))
    ns = ap.parse_args(list(argv))
    graph = _common.load_json(ns.graph)
    directions = _common.load_json(ns.directions)
    rng = random.Random(ns.seed)
    d = random_direction(directions, graph, rng)
    directions["directions"].append(d)
    _common.dump_json(ns.directions, directions)
    if ns.build:
        from build_preview import build
        build(directions, Path(ns.build), graph, _common.load_json(_common.KNOWLEDGE_DIR / "devices.json")["devices"])
    print(json.dumps({"id": d["id"], "name": d["name"], "style": d["bundle"]["style"], "ideas": d["bundle"]["ideas"], "layout": d["layout"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
