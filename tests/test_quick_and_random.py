import json
import random

import pytest

from _common import load_devices, load_graph, node_index
from build_preview import Prepared, build
from conftest import FIXTURES
from drafts import render
from quick_start import author_directions
from random_direction import random_direction
from validate_graph import validate_file


@pytest.fixture(scope="module")
def graph():
    return load_graph()


@pytest.fixture(scope="module")
def saas():
    return json.load(open(FIXTURES / "brief_saas.json", encoding="utf-8"))


def test_quick_start_authors_valid_directions(graph, saas):
    d = author_directions(saas, graph, 4)
    from _common import load_schema
    assert validate_file(d, "directions", load_schema()) == []
    assert len(d["directions"]) == 4 and all(x["bundle"]["ideas"] for x in d["directions"])
    assert len({x["id"] for x in d["directions"]}) == 4


def test_random_direction_is_seeded_and_valid(graph, saas):
    d = author_directions(saas, graph, 3)
    a = random_direction(d, graph, random.Random(3))
    b = random_direction(d, graph, random.Random(3))
    assert a == b
    assert a["bundle"]["style"] not in {x["bundle"]["style"] for x in d["directions"]}
    assert 8 <= len(a["bundle"]["ideas"]) <= 12
    hooks = [node_index(graph)[i].get("renders", "") for i in a["bundle"]["ideas"]]
    heroes = [h for h in hooks if h.startswith("hero-")]
    assert len(heroes) <= 1
    d["directions"].append(a)
    from _common import load_schema
    assert validate_file(d, "directions", load_schema()) == []


def test_random_direction_builds(tmp_path, graph, saas):
    d = author_directions(saas, graph, 3)
    d["directions"].append(random_direction(d, graph, random.Random(11)))
    report = build(d, tmp_path, graph, load_devices())
    assert (tmp_path / "R4" / "draft.html").exists() and not report["warnings"]


def test_topic_component_follows_product_type(graph, saas):
    idx = node_index(graph)
    d = author_directions(saas, graph, 3)["directions"][0]
    for pt, needle in (("product-type.developer-tool", 'data-variant="terminal"'), ("product-type.fintech", 'data-variant="balance"'),
                       ("product-type.event", 'data-variant="schedule"'), ("product-type.ai-product", 'data-variant="composer"')):
        brief = dict(saas, product_type=pt)
        html = render("marketing", Prepared(d, brief, idx))
        assert needle in html, pt
    brief = dict(saas, product_type="product-type.general-website")
    assert 'data-section="topic"' not in render("marketing", Prepared(d, brief, idx))


def test_gallery_has_surprise_me(tmp_path, graph, saas):
    d = author_directions(saas, graph, 3)
    build(d, tmp_path, graph, load_devices())
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert 'data-action="shuffle"' in html and "Surprise me" in html


def test_liveness_hooks_are_wired():
    from conftest import ROOT
    js = (ROOT / "skills/preview-first/assets/preview/preview.js").read_text(encoding="utf-8")
    css = (ROOT / "skills/preview-first/assets/preview/draft.css").read_text(encoding="utf-8")
    for hook in ("type-dot-matrix", "motion-char-reveal", "motion-scramble", "motion-variable-weight", "motion-velocity-skew", "motion-pointer-grid", "motion-trail"):
        assert hook in js, hook
    for cls in ("pfd-dotmatrix-canvas", "pfd-pointer-grid", "pfd-trail", "pfd-pinned", "pfd-hook-texture-stripes"):
        assert cls in css, cls
    assert "prefers-reduced-motion" in js and "pointer: fine" in js
