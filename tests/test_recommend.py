import json
from collections import Counter

import pytest

from conftest import FIXTURES, ROOT
from recommend import main, recommend, resolve_moods, resolve_product_type

GRAPH = ROOT / "skills" / "preview-first" / "knowledge" / "graph.json"


@pytest.fixture(scope="module")
def g():
    return json.load(open(GRAPH))


@pytest.fixture(scope="module")
def idx(g):
    return {n["id"]: n for n in g["nodes"]}


@pytest.fixture
def saas():
    return json.load(open(FIXTURES / "brief_saas.json"))


@pytest.fixture
def unknown():
    return json.load(open(FIXTURES / "brief_unknown.json"))


def _edge_exists(g, a, b, kind):
    return any(e["from"] == a and e["to"] == b and e["kind"] == kind for e in g["edges"])


def test_returns_requested_count_with_distinct_families(saas, g):
    b = recommend(saas, g, 4)
    assert len(b) == 4
    assert len({x["style_family"] for x in b}) == 4


def test_temperature_diversity(saas, g, idx):
    b = recommend(saas, g, 4)
    temps = Counter(idx[x["palette"]]["temperature"] for x in b)
    assert max(temps.values()) <= 2


def test_type_category_diversity(saas, g, idx):
    b = recommend(saas, g, 4)
    cats = Counter((idx[x["type_pairing"]]["heading"]["category"], idx[x["type_pairing"]]["body"]["category"]) for x in b)
    assert max(cats.values()) <= 2


def test_unknown_product_type_falls_back(unknown, g):
    assert resolve_product_type("dog grooming booking", g) == "product-type.local-business"
    assert resolve_product_type("something nobody has heard of", g) == "product-type.general-website"
    assert resolve_moods(["cozy", "sparkly", "warm"], g) == ["mood.cozy", "mood.warm"]
    b = recommend(unknown, g, 3)
    assert len(b) == 3


def test_dark_only_scheme_filters_palettes(saas, g, idx):
    saas["constraints"]["scheme"] = "dark"
    b = recommend(saas, g, 3)
    assert all(idx[x["palette"]]["scheme"] in ("dark", "both") for x in b)


def test_justification_cites_edges(saas, g):
    for x in recommend(saas, g, 4):
        assert x["justification"]
        assert all({"from", "to", "kind", "weight"} <= set(j) for j in x["justification"])


def test_alternatives_pair_with_style(saas, g):
    for x in recommend(saas, g, 4):
        assert x["alternatives"]["palettes"] and x["alternatives"]["type_pairings"]
        for pid in x["alternatives"]["palettes"]:
            assert _edge_exists(g, x["style"], pid, "pairs_with")
        assert x["palette"] not in x["alternatives"]["palettes"]


def test_bundle_shape(saas, g, idx):
    x = recommend(saas, g, 1)[0]
    assert set(x["treatments"]) == set(json.load(open(ROOT / "skills/preview-first/knowledge/schema.json"))["node_kinds"]["treatment"]["axis_values"])
    assert x["icon_set"].startswith("icon-set.")
    assert all(m.startswith("motion-pattern.") for m in x["motion"])
    assert x["motion_level"] in (0, 1, 2, 3)
    assert x["radius_scale"] == idx[x["style"]]["radius_scale"]


def test_motion_level_from_moods(saas, g):
    saas["moods"] = ["playful", "energetic"]
    assert recommend(saas, g, 1)[0]["motion_level"] == 2
    saas["moods"] = ["calm"]
    saas["product_type"] = "product-type.documentation"
    assert recommend(saas, g, 1)[0]["motion_level"] == 0
    saas["constraints"]["motion_level"] = 3
    assert recommend(saas, g, 1)[0]["motion_level"] == 3


def test_avoid_edges_lower_rank(g):
    brief = {"product": "A luxury watch atelier", "product_type": "product-type.luxury-commerce", "moods": ["premium", "quiet"], "page_type": "store", "constraints": {}}
    b = recommend(brief, g, 3)
    assert b[0]["style"] == "style.quiet-luxury"
    assert "style.playful-geometric" not in {x["style"] for x in b}


def test_list_cli_prints_ids(capsys):
    assert main(["--list", "moods"]) == 0
    out = capsys.readouterr().out
    assert "mood.calm" in out and "\t" in out


def test_brief_cli_prints_bundles(capsys):
    assert main(["--brief", str(FIXTURES / "brief_saas.json"), "--count", "3"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert len(out["bundles"]) == 3 and out["brief"]["product_type"] == "product-type.saas"


def test_deterministic(saas, g):
    assert recommend(saas, g, 4) == recommend(saas, g, 4)
