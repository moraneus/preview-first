import copy
import json
import re

import pytest

from _common import load_devices, load_graph, node_index
from build_preview import Prepared, build
from conftest import FIXTURES
from drafts import PAGE_TYPES, VARIANTS, default_copy, render, render_devices

EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿]")


@pytest.fixture(scope="module")
def directions():
    return json.load(open(FIXTURES / "directions_two.json", encoding="utf-8"))


@pytest.fixture(scope="module")
def idx():
    return node_index(load_graph())


def _prepared(directions, idx, which=0, layout=None, page_type=None):
    d = copy.deepcopy(directions["directions"][which])
    brief = dict(directions["brief"])
    if page_type:
        brief["page_type"] = page_type
    if layout is not None:
        d["layout"] = layout
    return Prepared(d, brief, idx)


def test_page_types_and_variants_declared():
    assert set(PAGE_TYPES) == {"marketing", "app", "content", "store"}
    assert {"split", "centered", "editorial", "product-first", "poster"} <= set(VARIANTS["marketing"]["hero"])
    assert {"bento", "list", "alternating", "columns"} <= set(VARIANTS["marketing"]["features"])
    assert set(VARIANTS["app"]["shell"]) == {"sidebar", "topbar"}
    assert set(VARIANTS["store"]["grid"]) == {"two", "three", "four"}


def test_each_page_type_renders_every_variant(directions, idx):
    for pt in PAGE_TYPES:
        for section, variants in VARIANTS[pt].items():
            for v in variants:
                html = render(pt, _prepared(directions, idx, 0, layout={section: v}, page_type=pt))
                assert 'data-section="%s"' % section in html, (pt, section)
                assert 'data-variant="%s"' % v in html, (pt, section, v)


def test_default_copy_has_no_tells():
    brief = {"product": "Pawfect, a dog grooming booking site for a neighbourhood salon", "product_type": "product-type.local-business", "page_type": "marketing", "words": {"name": "Pawfect"}}
    c = default_copy(brief)
    text = json.dumps(c)
    assert "—" not in text and "→" not in text and not EMOJI_RE.search(text)
    assert "lorem" not in text.lower()
    assert c["headline"] and c["cta_primary"] and len(c["features"]) == 3
    assert "Pawfect" in text


def test_two_styles_do_not_share_layout(directions, idx):
    a = _prepared(directions, idx, 0)
    b = _prepared(directions, idx, 1)
    ha, hb = render("marketing", a), render("marketing", b)
    assert ha != hb
    va = re.search(r'data-section="hero" data-variant="([a-z-]+)"', ha).group(1)
    vb = re.search(r'data-section="hero" data-variant="([a-z-]+)"', hb).group(1)
    assert va != vb


def test_draft_uses_brief_copy_not_placeholder(directions, idx):
    html = render("marketing", _prepared(directions, idx, 0))
    assert "Invoices that match your git log" in html
    assert "Pull requests become line items" in html
    assert "lorem" not in html.lower()


def test_devices_page_lists_defaults_and_frames(directions, idx):
    html = render_devices(_prepared(directions, idx, 0), load_devices())
    assert html.count('class="pf-device') >= 12
    assert 'data-cutout="island"' in html
    assert 'data-device-id="samsung-galaxy-z-fold7"' in html
    assert 'data-crease="1"' in html
    assert "Samsung" in html and "Apple" in html and "Google" in html
    assert 'input type="checkbox" data-device-id="iphone-17-pro-max" checked' in html
    assert "URLSearchParams" in html or "data-device-url" in html
    assert 'data-action="rotate"' in html


def test_devices_non_default_are_hidden(directions, idx):
    html = render_devices(_prepared(directions, idx, 0), load_devices())
    assert re.search(r'<figure class="pf-device[^"]*" hidden data-device-id="desktop-4k"', html) or 'hidden data-device-id="desktop-4k"' in html


def test_build_writes_draft_and_devices(tmp_path, directions):
    report = build(directions, tmp_path, load_graph(), load_devices())
    assert (tmp_path / "A/draft.html").exists() and (tmp_path / "A/devices.html").exists()
    html = (tmp_path / "A/devices.html").read_text(encoding="utf-8")
    assert "device-frames.css" in html


def test_draft_css_and_js_handle_safe_areas():
    from conftest import ROOT
    css = (ROOT / "skills/preview-first/assets/preview/draft.css").read_text(encoding="utf-8")
    js = (ROOT / "skills/preview-first/assets/preview/preview.js").read_text(encoding="utf-8")
    assert "--pf-safe-top" in css and "env(safe-area-inset-top)" in css
    assert 'sa-top' in js and "--pf-safe-" in js


# ---------------------------------------------------------------- non-generic archetypes

def test_new_hero_archetypes_exist():
    assert {"statement", "mark", "wrap", "product-first", "object", "bleed", "index"} <= set(VARIANTS["marketing"]["hero"])
    assert {"figures", "spec", "index", "bands"} <= set(VARIANTS["marketing"]["features"])
    assert "statement" in VARIANTS["marketing"]["proof"] and "giant" in VARIANTS["marketing"]["cta"] and "giant" in VARIANTS["marketing"]["footer"]


def test_no_default_layout_is_the_generic_template(idx):
    """No style may default to the centred hero plus bento/columns combination that reads as generated."""
    generic_heroes = {"centered"}
    for n in idx.values():
        if n["kind"] == "style":
            m = (n.get("layout_defaults") or {}).get("marketing", {})
            assert m.get("hero") not in generic_heroes, n["id"]


def test_drafts_render_art_not_wireframes(directions, idx):
    html = render("marketing", _prepared(directions, idx, 0))
    assert "<svg" in html and "pfd-art" in html
    assert 'class="pfd-media ' not in html or html.count('class="pfd-media ') <= 1


def test_statement_hero_has_two_tone_paragraph(directions, idx):
    html = render("marketing", _prepared(directions, idx, 0, layout={"hero": "statement"}))
    assert 'data-variant="statement"' in html and 'class="pfd-statement"' in html and "<em>" in html
