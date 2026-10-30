"""Turn a brief into ranked, diverse design-direction bundles by walking the knowledge graph.

Usage:
  recommend.py --brief brief.json [--count 4] [--graph PATH]
  recommend.py --list product-types|moods|styles|palettes|type-pairings|icon-sets
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _common  # noqa: E402

FALLBACK_PRODUCT = "product-type.general-website"
LIST_KINDS = {
    "ideas": "idea",
    "product-types": "product-type",
    "moods": "mood",
    "styles": "style",
    "palettes": "palette",
    "type-pairings": "type-pairing",
    "icon-sets": "icon-set",
}


# ---------------------------------------------------------------- graph access

class _Graph:
    def __init__(self, graph: dict):
        self.graph = graph
        self.idx = _common.node_index(graph)
        self.by_kind = _common.nodes_by_kind(graph)
        self.out: Dict[Tuple[str, str], List[dict]] = defaultdict(list)
        for e in graph.get("edges", []):
            self.out[(e["from"], e["kind"])].append(e)

    def edges(self, src: str, kind: str, dst_prefix: str = "") -> List[dict]:
        return [e for e in self.out.get((src, kind), []) if e["to"].startswith(dst_prefix) and e["to"] in self.idx]

    def weight(self, src: str, dst: str, kind: str) -> float:
        for e in self.out.get((src, kind), []):
            if e["to"] == dst:
                return float(e.get("weight", 0))
        return 0.0

    def edge(self, src: str, dst: str, kind: str) -> Optional[dict]:
        for e in self.out.get((src, kind), []):
            if e["to"] == dst:
                return e
        return None


def _tokens(text: str) -> List[str]:
    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if t]


# ---------------------------------------------------------------- resolving brief words

def resolve_product_type(text: str, graph: dict) -> str:
    """Exact id, then alias match, then token overlap, then the general fallback."""
    g = graph if isinstance(graph, _Graph) else _Graph(graph)
    text = (text or "").strip()
    if text in g.idx and g.idx[text]["kind"] == "product-type":
        return text
    low = text.lower()
    nodes = g.by_kind.get("product-type", [])
    for n in nodes:
        if low == n["name"].lower() or low in [a.lower() for a in n.get("aliases", [])]:
            return n["id"]
    toks = set(_tokens(low))
    best, best_score = None, 0
    for n in sorted(nodes, key=lambda x: x["id"]):
        words = set(_tokens(n["name"]))
        for a in n.get("aliases", []):
            words |= set(_tokens(a))
        score = len(toks & words)
        if score > best_score:
            best, best_score = n["id"], score
    return best if best and best_score > 0 else FALLBACK_PRODUCT


def resolve_moods(words: Sequence[str], graph: dict) -> List[str]:
    """Map free mood words to mood ids; unknown words are dropped, order kept, no duplicates."""
    g = graph if isinstance(graph, _Graph) else _Graph(graph)
    out: List[str] = []
    for w in words or []:
        w_low = str(w).lower().strip()
        if w_low in g.idx and g.idx[w_low]["kind"] == "mood":
            hit = w_low
        else:
            hit = None
            for n in g.by_kind.get("mood", []):
                if w_low == n["name"].lower() or w_low in [a.lower() for a in n.get("aliases", [])]:
                    hit = n["id"]
                    break
        if hit and hit not in out:
            out.append(hit)
    return out


# ---------------------------------------------------------------- scoring

def _style_scores(g: _Graph, product: str, moods: List[str]) -> Tuple[Dict[str, float], Dict[str, List[dict]]]:
    scores: Dict[str, float] = {}
    why: Dict[str, List[dict]] = defaultdict(list)
    for s in g.by_kind.get("style", []):
        sid = s["id"]
        total = 0.0
        e = g.edge(product, sid, "suits")
        if e:
            total += float(e["weight"])
            why[sid].append(e)
        e = g.edge(product, sid, "avoid_with")
        if e:
            total -= float(e["weight"])
            why[sid].append(e)
        for m in moods:
            e = g.edge(m, sid, "expresses")
            if e:
                total += 0.7 * float(e["weight"])
                why[sid].append(e)
            e = g.edge(m, sid, "avoid_with")
            if e:
                total -= float(e["weight"])
                why[sid].append(e)
        scores[sid] = total
    return scores, why


def _candidates(g: _Graph, style: str, prefix: str, moods: List[str], scheme: Optional[str]) -> List[Tuple[str, float, dict]]:
    """Ranked (id, score, edge) for palettes or pairings that pair with a style."""
    hints = [g.idx[m].get("temperature_hint") for m in moods if m in g.idx]
    out = []
    for e in g.edges(style, "pairs_with", prefix):
        node = g.idx[e["to"]]
        score = float(e["weight"])
        if prefix == "palette.":
            if scheme == "dark" and node.get("scheme") == "light":
                continue
            if scheme == "light" and node.get("scheme") == "dark":
                continue
            if node.get("temperature") in hints:
                score += 0.3
        if g.edge(style, e["to"], "avoid_with"):
            continue
        for m in moods:
            if g.edge(m, e["to"], "avoid_with"):
                score -= 1.0
        live = node.get("live") or {}
        if live.get("trending"):
            score += 0.05
        out.append((e["to"], score, e))
    out.sort(key=lambda t: (-t[1], t[0]))
    return out


def _motion_level(g: _Graph, brief: dict, product: str, moods: List[str]) -> int:
    forced = (brief.get("constraints") or {}).get("motion_level")
    if isinstance(forced, int) and not isinstance(forced, bool):
        return max(0, min(3, forced))
    levels = [g.idx[m].get("motion_level") for m in moods if m in g.idx and g.idx[m].get("motion_level") is not None]
    if not levels:
        return 1
    level = max(levels)
    if product == "product-type.documentation" and min(levels) == 0:
        level = 0
    return int(level)


def _pair_key(g: _Graph, pairing_id: str) -> Tuple[str, str]:
    n = g.idx[pairing_id]
    return (n["heading"]["category"], n["body"]["category"])


# ---------------------------------------------------------------- ideas

IDEA_SLOTS = [
    ("navigation",), ("hero",), ("typography", "craft"), ("section", "layout"), ("imagery", "art", "colour", "texture"),
    ("motion", "interaction", "cursor", "scroll", "loading"), ("footer", "component", "copy"),
]
EXCLUSIVE_PREFIXES = ("nav-", "hero-", "texture-", "features-", "footer-", "proof-", "cta-")
IDEAS_PER_BUNDLE = 10


def _idea_scores(g: _Graph, style: dict, product: str, moods: List[str], page_type: str) -> List[Tuple[str, float]]:
    sid = style["id"]
    defaults = list(style.get("ideas") or [])
    out = []
    for n in g.by_kind.get("idea", []):
        iid = n["id"]
        if g.edge(iid, sid, "avoid_with") or any(g.edge(m, iid, "avoid_with") for m in moods):
            continue
        pts = n.get("page_types")
        if pts and page_type not in pts:
            continue
        score = 0.0
        if iid in defaults:
            score += 2.0 - defaults.index(iid) * 0.05
        e = g.edge(iid, sid, "pairs_with")
        if e:
            score += float(e["weight"])
        e = g.edge(product, iid, "suits")
        if e:
            score += 0.6 * float(e["weight"])
        for m in moods:
            e = g.edge(m, iid, "expresses")
            if e:
                score += 0.4 * float(e["weight"])
        if n.get("ai_tell_risk") == "high" and iid not in defaults:
            continue
        if n.get("ai_tell_risk") == "medium":
            score -= 0.25
        if score < 0 or (score == 0 and n.get("ai_tell_risk") != "low"):
            continue
        out.append((iid, score))
    out.sort(key=lambda t: (-t[1], t[0]))
    return out


def _ideas_for(g: _Graph, style: dict, product: str, moods: List[str], page_type: str,
               used_hooks: set, used_ideas: set, count: int = IDEAS_PER_BUNDLE) -> List[str]:
    """Pick ideas for one direction: one per hook, category coverage, and no nav, hero, texture or
    section device shared with another direction in the set."""
    ranked = _idea_scores(g, style, product, moods, page_type)
    chosen: List[str] = []
    hooks_here: set = set()

    def ok(iid: str, strict: bool) -> bool:
        n = g.idx[iid]
        hook = n.get("renders")
        if iid in chosen:
            return False
        if hook:
            if hook in hooks_here:
                return False
            prefix = hook.split("-", 1)[0] + "-"
            if prefix in ("hero-", "nav-", "footer-", "proof-", "cta-") and any(h.startswith(prefix) for h in hooks_here):
                return False
            if strict and hook.startswith(EXCLUSIVE_PREFIXES) and hook in used_hooks:
                return False
        if strict and iid in used_ideas and n["category"] in ("hero", "navigation"):
            return False
        return True

    def take(iid: str) -> None:
        chosen.append(iid)
        hook = g.idx[iid].get("renders")
        if hook:
            hooks_here.add(hook)

    for slot in IDEA_SLOTS:
        allow_zero = slot in (("navigation",), ("typography", "craft"))  # every direction gets a nav device and one type craft; other slots need a real fit
        pick = next((iid for iid, sc in ranked if g.idx[iid]["category"] in slot and (sc > 0 or allow_zero) and ok(iid, True)), None)
        if pick is None and allow_zero:
            pick = next((iid for iid, sc in ranked if g.idx[iid]["category"] in slot and ok(iid, False)), None)
        if pick:
            take(pick)
    for iid, score in ranked:
        if len(chosen) >= count:
            break
        if score > 0 and ok(iid, True):
            take(iid)
    if len(chosen) < 6:  # pad with quiet craft ideas (no hero, nav or section device) that fit a mood or product
        for iid, score in ranked:
            if len(chosen) >= 6:
                break
            n = g.idx[iid]
            hook = n.get("renders")
            if score > 0 and n["category"] in ("craft", "typography", "motion", "component") and (not hook or not hook.startswith(EXCLUSIVE_PREFIXES)) and ok(iid, True):
                take(iid)
    used_hooks.update(h for h in hooks_here if h.startswith(EXCLUSIVE_PREFIXES))
    used_ideas.update(chosen)
    return chosen


# ---------------------------------------------------------------- main entry

def recommend(brief: dict, graph: dict, count: int = 4) -> List[dict]:
    g = _Graph(graph)
    product = resolve_product_type(brief.get("product_type", ""), g)
    moods = resolve_moods(brief.get("moods", []), g)
    scheme = (brief.get("constraints") or {}).get("scheme")
    motion_level = _motion_level(g, brief, product, moods)

    scores, why = _style_scores(g, product, moods)
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    page_type = brief.get("page_type", "marketing")
    used_hooks: set = set()
    used_ideas: set = set()

    bundles: List[dict] = []
    families_used: set = set()
    # At least two directions must come from styles marked "distinct" (not the familiar SaaS
    # looks), so a set never reads as the generic template in different colours.
    distinct_needed = 2 if count >= 3 else 1
    temp_count: Counter = Counter()
    cat_count: Counter = Counter()
    relax = 0  # 0 strict, 1 drop temperature rule, 2 drop category rule, 3 drop family rule

    while len(bundles) < count and relax <= 3:
        progressed = False
        for sid, score in ranked:
            if len(bundles) >= count:
                break
            if any(b["style"] == sid for b in bundles):
                continue
            style = g.idx[sid]
            if relax < 3 and style["family"] in families_used:
                continue
            distinct_have = sum(1 for b in bundles if g.idx[b["style"]].get("conventionality") == "distinct")
            slots_left = count - len(bundles)
            if relax < 3 and style.get("conventionality") != "distinct" and (distinct_needed - distinct_have) >= slots_left:
                continue
            palettes = _candidates(g, sid, "palette.", moods, scheme)
            pairings = _candidates(g, sid, "type-pairing.", moods, None)
            if not palettes or not pairings:
                continue
            used_pal = {b["palette"] for b in bundles}
            used_pair = {b["type_pairing"] for b in bundles}
            pal = next((p for p in palettes if p[0] not in used_pal
                        and (relax >= 1 or temp_count[g.idx[p[0]]["temperature"]] < 2)), None)
            pair = next((p for p in pairings if p[0] not in used_pair
                         and (relax >= 2 or cat_count[_pair_key(g, p[0])] < 2)), None)
            if pal is None or pair is None:
                continue
            treatments = {}
            for e in g.edges(sid, "defaults_to", "treatment."):
                t = g.idx[e["to"]]
                treatments[t["axis"]] = t["value"]
            motion = sorted(
                e["to"] for e in g.edges(sid, "defaults_to", "motion-pattern.")
                if g.idx[e["to"]]["level"] <= motion_level
            )
            if motion_level == 0:
                motion = ["motion-pattern.none"]
            icons = g.edges(sid, "pairs_with", "icon-set.")
            icons.sort(key=lambda e: (-float(e["weight"]), e["to"]))
            icon = icons[0]["to"] if icons else "icon-set.lucide"
            justification = [dict(e) for e in why.get(sid, [])] + [dict(pal[2]), dict(pair[2])]
            if icons:
                justification.append(dict(icons[0]))
            ideas = _ideas_for(g, style, product, moods, page_type, used_hooks, used_ideas)
            bundles.append({
                "style": sid,
                "style_family": style["family"],
                "palette": pal[0],
                "type_pairing": pair[0],
                "treatments": treatments,
                "motion": motion,
                "motion_level": motion_level,
                "icon_set": icon,
                "ideas": ideas,
                "radius_scale": style["radius_scale"],
                "density": style["density"],
                "alternatives": {
                    "palettes": [p[0] for p in palettes if p[0] != pal[0]][:5],
                    "type_pairings": [p[0] for p in pairings if p[0] != pair[0]][:5],
                    "icon_sets": [e["to"] for e in icons[1:]] or [i["id"] for i in g.by_kind.get("icon-set", []) if i["id"] != icon][:3],
                },
                "justification": justification,
                "score": round(score, 3),
            })
            families_used.add(style["family"])
            temp_count[g.idx[pal[0]]["temperature"]] += 1
            cat_count[_pair_key(g, pair[0])] += 1
            progressed = True
        if not progressed or len(bundles) < count:
            relax += 1
    return bundles


def normalise_brief(brief: dict, graph: dict) -> dict:
    """Return a copy of the brief with product_type and moods mapped to node ids."""
    out = dict(brief)
    out["product_type"] = resolve_product_type(brief.get("product_type", ""), graph)
    out["moods"] = resolve_moods(brief.get("moods", []), graph)
    return out


# ---------------------------------------------------------------- CLI

def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Recommend design directions from a brief.")
    ap.add_argument("--brief")
    ap.add_argument("--count", type=int, default=4)
    ap.add_argument("--graph", default=str(_common.KNOWLEDGE_DIR / "graph.json"))
    ap.add_argument("--list", choices=sorted(LIST_KINDS))
    ns = ap.parse_args(list(argv))
    graph = _common.load_json(ns.graph)
    try:  # annotate with live data when a snapshot exists (bundled or user cache)
        from refresh_knowledge import annotate_graph, load_live
        live = load_live()
        if live:
            graph = annotate_graph(graph, live)
    except Exception:  # live data is optional
        pass
    if ns.list:
        kind = LIST_KINDS[ns.list]
        for n in sorted(_common.nodes_by_kind(graph).get(kind, []), key=lambda x: x["id"]):
            aliases = ", ".join(n.get("aliases", [])) if "aliases" in n else n.get("summary", n.get("notes", ""))
            if kind == "idea":
                aliases = "%s | %s | %s" % (n.get("category", ""), n.get("renders") or "contract-only", n.get("what", "")[:110])
            print("%s\t%s\t%s" % (n["id"], n["name"], aliases))
        return 0
    if not ns.brief:
        ap.error("--brief or --list is required")
    brief = _common.load_json(ns.brief)
    bundles = recommend(brief, graph, max(1, min(5, ns.count)))
    print(json.dumps({"brief": normalise_brief(brief, graph), "bundles": bundles}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
