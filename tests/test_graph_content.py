"""Content-level checks on the shipped knowledge graph."""
import json

import pytest

from conftest import ROOT
from validate_graph import validate

GRAPH_PATH = ROOT / "skills" / "preview-first" / "knowledge" / "graph.json"
SCHEMA_PATH = ROOT / "skills" / "preview-first" / "knowledge" / "schema.json"


@pytest.fixture(scope="module")
def graph():
    return json.load(open(GRAPH_PATH))


@pytest.fixture(scope="module")
def schema():
    return json.load(open(SCHEMA_PATH))


@pytest.fixture(scope="module")
def by(graph):
    out = {}
    for n in graph["nodes"]:
        out.setdefault(n["kind"], []).append(n)
    return out


def _edges(graph, src=None, kind=None, dst_prefix=None):
    for e in graph["edges"]:
        if src and e["from"] != src:
            continue
        if kind and e["kind"] != kind:
            continue
        if dst_prefix and not e["to"].startswith(dst_prefix):
            continue
        yield e


def test_counts(by):
    assert len(by["style"]) >= 14
    assert len(by["treatment"]) >= 30
    assert len(by["motion-pattern"]) >= 25
    assert len(by["product-type"]) >= 20
    assert len(by["mood"]) >= 18
    assert len(by["icon-set"]) >= 6
    assert len(by["platform-feature"]) >= 12


def test_style_families_cover_all_seven(by):
    assert {s["family"] for s in by["style"]} == {"minimal", "editorial", "technical", "soft", "expressive", "dark", "bold"}


def test_every_style_has_full_treatment_defaults(graph, by, schema):
    axes = set(schema["node_kinds"]["treatment"]["axis_values"])
    idx = {n["id"]: n for n in graph["nodes"]}
    for s in by["style"]:
        covered = {idx[e["to"]]["axis"] for e in _edges(graph, s["id"], "defaults_to", "treatment.")}
        assert covered == axes, "%s misses %s" % (s["id"], axes - covered)


def test_every_style_has_motion_defaults_at_levels_one_and_two(graph, by):
    idx = {n["id"]: n for n in graph["nodes"]}
    for s in by["style"]:
        levels = {idx[e["to"]]["level"] for e in _edges(graph, s["id"], "defaults_to", "motion-pattern.")}
        assert {1, 2} <= levels, s["id"]


def test_every_style_has_icon_set_and_layout_defaults(graph, by):
    for s in by["style"]:
        assert list(_edges(graph, s["id"], "pairs_with", "icon-set.")), s["id"]
        assert "marketing" in s["layout_defaults"], s["id"]


def test_every_product_type_suits_at_least_three_styles(graph, by):
    for p in by["product-type"]:
        assert len(list(_edges(graph, p["id"], "suits", "style."))) >= 3, p["id"]


def test_every_mood_expresses_at_least_two_styles(graph, by):
    for m in by["mood"]:
        assert len(list(_edges(graph, m["id"], "expresses", "style."))) >= 2, m["id"]


def test_general_website_fallback_exists(by):
    assert any(p["id"] == "product-type.general-website" for p in by["product-type"])


def test_motion_none_exists_and_levels_span(by):
    ids = {m["id"] for m in by["motion-pattern"]}
    assert "motion-pattern.none" in ids
    assert {m["level"] for m in by["motion-pattern"]} == {0, 1, 2, 3}


def test_validator_has_no_errors(graph, schema):
    errors = [f for f in validate(graph, schema) if f.level == "error"]
    assert errors == [], errors[:10]
