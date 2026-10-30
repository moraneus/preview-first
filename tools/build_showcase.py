"""Build a showcase preview with one direction per style (every template the skill ships).

uv run python3 tools/build_showcase.py OUT_DIR [--page-type marketing]
"""
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/preview-first/scripts"))
import _common
from recommend import _Graph, _candidates, _ideas_for

BRIEF = {"product": "Northwind, a weather service for sailors", "audience": "skippers and coastal crews who plan by the tide",
         "product_type": "product-type.saas", "moods": ["mood.confident", "mood.precise"], "page_type": "marketing",
         "constraints": {"scheme": "both"}, "words": {"name": "Northwind", "tagline": "Know the sea before you leave the harbour"}}


def main(out: str, page_type: str = "marketing"):
    graph = _common.load_graph(); g = _Graph(graph)
    brief = dict(BRIEF, page_type=page_type)
    dirs = []
    used_hooks, used_ideas = set(), set()
    styles = sorted(g.by_kind["style"], key=lambda s: s["id"])
    for i, st in enumerate(styles):
        pal = _candidates(g, st["id"], "palette.", [], None)[0][0]
        pair = _candidates(g, st["id"], "type-pairing.", [], None)[0][0]
        treatments = {g.idx[e["to"]]["axis"]: g.idx[e["to"]]["value"] for e in g.edges(st["id"], "defaults_to", "treatment.")}
        motion = sorted(e["to"] for e in g.edges(st["id"], "defaults_to", "motion-pattern.") if g.idx[e["to"]]["level"] <= 2)
        icons = g.edges(st["id"], "pairs_with", "icon-set.")
        ideas = _ideas_for(g, st, "product-type.saas", [], page_type, set(), set())  # per style, no cross-direction exclusivity
        dirs.append({"id": "S%02d" % (i + 1), "name": st["name"], "rationale": st["summary"],
                     "bundle": {"style": st["id"], "style_family": st["family"], "palette": pal, "type_pairing": pair, "treatments": treatments,
                                "motion": motion, "motion_level": 2, "icon_set": icons[0]["to"] if icons else "icon-set.lucide", "ideas": ideas,
                                "radius_scale": st["radius_scale"], "density": st["density"], "alternatives": {"palettes": [], "type_pairings": [], "icon_sets": []}}})
    directions = {"version": 1, "brief": brief, "directions": dirs}
    Path(out).mkdir(parents=True, exist_ok=True)
    _common.dump_json(Path(out) / "directions.json", directions)
    subprocess.check_call([sys.executable, str(ROOT / "skills/preview-first/scripts/build_preview.py"), "--directions", str(Path(out) / "directions.json"), "--out", str(Path(out) / "preview")])
    print(json.dumps([(d["id"], d["bundle"]["style"]) for d in dirs]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "marketing")
