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
        if section == "programme":
            layout["programme"] = rng.choice(options)
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


def variation_of(directions: dict, graph: dict, base_id: str, rng: random.Random) -> dict:
    """Same style as the base direction, other palette, pairing, ideas, variants and programme."""
    g = _Graph(graph)
    base = next((d for d in directions["directions"] if d["id"] == base_id), None)
    if base is None:
        raise KeyError(base_id)
    brief = directions.get("brief", {})
    product = resolve_product_type(brief.get("product_type", ""), g)
    moods = resolve_moods(brief.get("moods", []), g)
    page_type = brief.get("page_type", "marketing")
    style = g.idx[base["bundle"]["style"]]
    pals = [x for x in _candidates(g, style["id"], "palette.", moods, (brief.get("constraints") or {}).get("scheme")) if x[0] != base["bundle"]["palette"]] or _candidates(g, style["id"], "palette.", moods, None)
    pairs = [x for x in _candidates(g, style["id"], "type-pairing.", moods, None) if x[0] != base["bundle"]["type_pairing"]] or _candidates(g, style["id"], "type-pairing.", moods, None)
    d = random_direction({"brief": brief, "directions": []}, graph, rng)
    d["bundle"]["style"] = style["id"]
    d["bundle"]["style_family"] = style["family"]
    d["bundle"]["palette"] = rng.choice(pals[:6])[0] if pals else base["bundle"]["palette"]
    d["bundle"]["type_pairing"] = rng.choice(pairs[:6])[0] if pairs else base["bundle"]["type_pairing"]
    d["bundle"]["treatments"] = dict(base["bundle"].get("treatments", {}))
    d["bundle"]["icon_set"] = base["bundle"].get("icon_set", d["bundle"]["icon_set"])
    ranked = _idea_scores(g, style, product, moods, page_type)
    pool = [iid for iid, sc in ranked if sc > 0]
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
        if len(chosen) >= 10:
            break
    d["bundle"]["ideas"] = chosen
    n = len(directions["directions"]) + 1
    d["id"] = "V%d" % n
    d["name"] = "%s, take %d" % (base.get("name", style["name"]), n)
    d["rationale"] = "A variation of %s: same style, another palette, pairing, set of ideas and page programme." % base.get("name", style["name"])
    d["copy"] = dict(base.get("copy") or {})
    return d


def all_styles(directions: dict, graph: dict) -> list:
    """One direction per style not yet in the set, each with its own defaults and fitting ideas."""
    from recommend import _ideas_for
    g = _Graph(graph)
    brief = directions.get("brief", {})
    product = resolve_product_type(brief.get("product_type", ""), g)
    moods = resolve_moods(brief.get("moods", []), g)
    page_type = brief.get("page_type", "marketing")
    used = {d["bundle"]["style"] for d in directions["directions"]}
    out = []
    n = len(directions["directions"])
    copy = dict(directions["directions"][0].get("copy") or {}) if directions["directions"] else {}
    for style in sorted(g.by_kind["style"], key=lambda s: s["id"]):
        if style["id"] in used:
            continue
        pals = _candidates(g, style["id"], "palette.", moods, (brief.get("constraints") or {}).get("scheme")) or _candidates(g, style["id"], "palette.", moods, None)
        pairs = _candidates(g, style["id"], "type-pairing.", moods, None)
        if not pals or not pairs:
            continue
        n += 1
        treatments = {g.idx[e["to"]]["axis"]: g.idx[e["to"]]["value"] for e in g.edges(style["id"], "defaults_to", "treatment.")}
        motion = sorted(e["to"] for e in g.edges(style["id"], "defaults_to", "motion-pattern.") if g.idx[e["to"]]["level"] <= 2)
        icons = g.edges(style["id"], "pairs_with", "icon-set.")
        out.append({"id": "S%d" % n, "name": style["name"], "rationale": style.get("summary", ""), "copy": copy,
                    "bundle": {"style": style["id"], "style_family": style["family"], "palette": pals[0][0], "type_pairing": pairs[0][0], "treatments": treatments,
                               "motion": motion or ["motion-pattern.none"], "motion_level": 2, "icon_set": icons[0]["to"] if icons else "icon-set.lucide",
                               "ideas": _ideas_for(g, style, product, moods, page_type, set(), set()), "radius_scale": style["radius_scale"], "density": style["density"],
                               "alternatives": {"palettes": [x[0] for x in pals[1:6]], "type_pairings": [x[0] for x in pairs[1:6]], "icon_sets": []}}})
    return out


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Append a random direction.")
    ap.add_argument("--directions", required=True)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--build", help="preview directory to rebuild after adding")
    ap.add_argument("--graph", default=str(_common.KNOWLEDGE_DIR / "graph.json"))
    ap.add_argument("--like", metavar="ID", help="five variations of this direction instead of a random draw")
    ap.add_argument("--all", action="store_true", help="one direction per style not yet in the set")
    ns = ap.parse_args(list(argv))
    graph = _common.load_json(ns.graph)
    directions = _common.load_json(ns.directions)
    rng = random.Random(ns.seed)
    if ns.all:
        added = all_styles(directions, graph)
    elif ns.like:
        added = []
        for _ in range(5):
            v = variation_of({"brief": directions["brief"], "directions": directions["directions"] + added}, graph, ns.like, rng)
            added.append(v)
    else:
        added = [random_direction(directions, graph, rng)]
    directions["directions"].extend(added)
    _common.dump_json(ns.directions, directions)
    if ns.build:
        from build_preview import build
        build(directions, Path(ns.build), graph, _common.load_json(_common.KNOWLEDGE_DIR / "devices.json")["devices"])
    print(json.dumps([{"id": d["id"], "name": d["name"], "style": d["bundle"]["style"]} for d in added], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
