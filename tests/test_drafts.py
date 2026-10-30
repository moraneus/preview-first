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
    assert {"sidebar", "topbar", "rail", "bottom-tabs", "none"} <= set(VARIANTS["app"]["shell"])
    assert {"table", "ledger", "board", "cards", "kanban", "feed"} <= set(VARIANTS["app"]["view"])
    assert {"two", "three", "four", "editorial"} <= set(VARIANTS["store"]["grid"])
    assert {"lookbook", "tiles"} <= set(VARIANTS["store"]["hero"]) and {"broadsheet"} <= set(VARIANTS["content"]["header"])
    assert {"ticker", "specimen", "manifesto", "numbers", "clip", "stacked"} <= set(VARIANTS["marketing"]["hero"])
    assert {"numerals", "stack", "strip", "hover-list", "cells", "accordion"} <= set(VARIANTS["marketing"]["features"])


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
    assert c["headline"] and c["cta_primary"] and len(c["features"]) >= 3
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


def test_survey_archetypes_added():
    assert {"collage", "letter"} <= set(VARIANTS["marketing"]["hero"])
    assert "ledger" in VARIANTS["marketing"]["features"]


def test_ledger_rows_and_collage_render(directions, idx):
    html = render("marketing", _prepared(directions, idx, 0, layout={"hero": "collage", "features": "ledger"}))
    assert 'data-variant="collage"' in html and html.count("pfd-collage-item") >= 4
    assert 'data-variant="ledger"' in html and html.count("pfd-ledger-row") >= 3 and "pfd-ledger-count" in html
    html = render("marketing", _prepared(directions, idx, 0, layout={"hero": "letter"}))
    assert 'data-variant="letter"' in html and "pfd-letter" in html


# ---------------------------------------------------------------- render hooks (0.3.0)

def test_hooks_change_nav_texture_and_sections(directions, idx):
    d = copy.deepcopy(directions["directions"][0])
    d["bundle"]["ideas"] = ["idea.split-nav-live-meta", "idea.film-grain", "idea.giant-numerals-features", "idea.colophon-footer", "idea.marquee-divider", "idea.outline-giant-word"]
    d["layout"] = {}  # the fixture pins every section by hand; hooks only fill what the author left open
    p = Prepared(d, directions["brief"], idx)
    assert {"nav-split-meta", "texture-grain", "features-numerals", "footer-colophon", "section-marquee", "type-outline"} <= p.hooks
    html = render("marketing", p)
    assert 'data-variant="split-meta"' in html and "data-live-time" in html
    assert 'class="pfd-grain"' in html and 'pfd-hook-texture-grain' in html
    assert 'data-section="features" data-variant="numerals"' in html
    assert 'data-section="footer" data-variant="colophon"' in html and "Set in " in html
    assert 'class="pfd-marquee"' in html and 'class="pfd-outline"' in html


def test_explicit_layout_beats_hooks(directions, idx):
    d = copy.deepcopy(directions["directions"][0])
    d["bundle"]["ideas"] = ["idea.giant-numerals-features"]
    d["layout"] = {"features": "spec"}
    html = render("marketing", Prepared(d, directions["brief"], idx))
    assert 'data-section="features" data-variant="spec"' in html


def test_numbers_hero_never_invents_figures(directions, idx):
    d = copy.deepcopy(directions["directions"][0])
    d["bundle"]["ideas"] = ["idea.numbers-hero"]
    d["layout"] = {"hero": "numbers"}
    html = render("marketing", Prepared(d, directions["brief"], idx))
    assert 'data-variant="numbers"' in html and "pfd-big-num" not in html
    d["copy"]["numbers"] = [{"value": "1,200", "label": "developers"}, {"value": "40", "label": "countries"}, {"value": "4", "label": "minutes per invoice"}]
    html = render("marketing", Prepared(d, directions["brief"], idx))
    assert html.count("pfd-big-num") == 3


def test_colour_blocking_and_inverted_ending(directions, idx):
    d = copy.deepcopy(directions["directions"][0])
    d["bundle"]["ideas"] = ["idea.inverted-closing-section"]
    html = render("marketing", Prepared(d, directions["brief"], idx))
    assert html.count("pfd-block-ink") == 2


def test_store_content_app_variants_render(directions, idx):
    for pt, layout, needle in (("store", {"hero": "lookbook", "grid": "editorial", "product": "sticky-buy"}, "pfd-lookbook"),
                               ("content", {"header": "broadsheet", "article": "side-notes", "list": "archive"}, "pfd-broadsheet"),
                               ("app", {"shell": "rail", "view": "ledger", "detail": "inspector"}, "pfd-shell-rail"),
                               ("app", {"shell": "none", "view": "board"}, "pfd-board-figure"),
                               ("app", {"shell": "bottom-tabs", "view": "cards"}, "pfd-bottom-tabs"),
                               ("app", {"shell": "topbar", "view": "kanban"}, "pfd-kanban"),
                               ("app", {"shell": "sidebar", "view": "feed"}, "pfd-feed")):
        html = render(pt, _prepared(directions, idx, 0, layout=layout, page_type=pt))
        assert needle in html, pt


def test_headline_decoration_escapes_every_word(directions, idx):
    d = copy.deepcopy(directions["directions"][0])
    d["bundle"]["ideas"] = ["idea.outline-giant-word"]
    d["layout"] = {}
    d["copy"] = dict(d["copy"], headline="Invoices <span onclick=x> <script>alert(1)</script>")
    html = render("marketing", Prepared(d, directions["brief"], idx))
    assert "<script>" not in html and "<span onclick" not in html


def test_showcase_variants_render(directions, idx):
    for hero in ("split-screen", "diagonal", "mosaic", "kinetic", "fan"):
        html = render("marketing", _prepared(directions, idx, 0, layout={"hero": hero}))
        assert 'data-section="hero" data-variant="%s"' % hero in html
    html = render("marketing", _prepared(directions, idx, 0, layout={"features": "mosaic"}))
    assert "pfd-mo-grid" in html


def test_style_default_ideas_win_over_other_hooks(directions, idx):
    d = copy.deepcopy(directions["directions"][0])
    d["layout"] = {}
    # the fixture style (paper-editorial) lists hairline-accordion among its own ideas; a stacking-cards idea from elsewhere must not override it
    d["bundle"]["ideas"] = ["idea.stacking-cards", "idea.hairline-accordion"]
    html = render("marketing", Prepared(d, directions["brief"], idx))
    assert 'data-section="features" data-variant="accordion"' in html


def test_borrowed_hero_hook_does_not_replace_the_style_hero(directions, idx):
    d = copy.deepcopy(directions["directions"][0])
    d["layout"] = {}
    d["bundle"]["ideas"] = ["idea.type-specimen-hero"]  # not among paper-editorial's own ideas
    html = render("marketing", Prepared(d, directions["brief"], idx))
    assert 'data-section="hero" data-variant="editorial"' in html


def test_app_board_figure_comes_from_the_brief(directions, idx):
    d = copy.deepcopy(directions["directions"][0])
    brief = dict(directions["brief"], page_type="app")
    d["layout"] = {"shell": "none", "view": "board"}
    d["copy"] = dict(d["copy"], headline="Live scores for 501 and Cricket")
    html = render("app", Prepared(d, brief, idx))
    assert 'data-count="501"' in html
