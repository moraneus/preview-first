import json
import re
from html.parser import HTMLParser

import pytest

from _common import load_devices, load_graph
from build_preview import build, main, render_template
from conftest import FIXTURES, ROOT

ASSETS = ROOT / "skills/preview-first/assets/preview"


class _Hooks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def _parse(path):
    p = _Hooks()
    p.feed(path.read_text(encoding="utf-8"))
    return p.tags


def _count(tags, tag=None, **attrs):
    n = 0
    for t, a in tags:
        if tag and t != tag:
            continue
        if all(a.get(k) == v if v is not None else k in a for k, v in attrs.items()):
            n += 1
    return n


@pytest.fixture(scope="module")
def out(tmp_path_factory):
    d = tmp_path_factory.mktemp("preview")
    directions = json.load(open(FIXTURES / "directions_two.json", encoding="utf-8"))
    report = build(directions, d, load_graph(), load_devices())
    return d, report


def test_build_writes_expected_files(out):
    d, report = out
    for rel in ["index.html", "A/tile.html", "B/tile.html", "A/tokens.css", "A/variants.css",
                "assets/preview.css", "assets/tile.css", "assets/preview.js", "assets/device-frames.css", "data.json"]:
        assert (d / rel).exists(), rel
    assert any(p.endswith("index.html") for p in report["pages"])


def test_gallery_lists_both_directions(out):
    d, _ = out
    html = (d / "index.html").read_text(encoding="utf-8")
    assert "Ledger" in html and "Console" in html
    tags = _parse(d / "index.html")
    assert _count(tags, "article", **{"data-direction": "A"}) == 1
    assert _count(tags, "article", **{"data-direction": "B"}) == 1
    assert _count(tags, "button", **{"data-action": "select"}) >= 2


def test_tile_has_all_sections(out):
    d, _ = out
    tags = _parse(d / "A/tile.html")
    for section in ["palette", "type", "spacing", "radius", "elevation", "icons", "components", "motion"]:
        assert _count(tags, "section", **{"data-section": section}) == 1, section


def test_tile_palette_swatches_and_contrast(out):
    d, _ = out
    tags = _parse(d / "A/tile.html")
    assert _count(tags, **{"data-role": None}) >= 14
    html = (d / "A/tile.html").read_text(encoding="utf-8")
    assert "pf-contrast" in html and "oklch(" in html and re.search(r"#[0-9a-f]{6}", html)


def test_tile_components_states(out):
    d, _ = out
    tags = _parse(d / "A/tile.html")
    states = {a.get("data-state") for t, a in tags if t == "button" and "pf-btn" in a.get("class", "")}
    assert {"default", "hover", "focus", "active", "disabled", "loading"} <= states
    input_states = {a.get("data-state") for t, a in tags if t == "input" and a.get("type") == "text"}
    assert {"default", "focus", "error", "disabled"} <= input_states


def test_tile_motion_demos_match_bundle(out):
    d, _ = out
    tags = _parse(d / "A/tile.html")
    ids = {a.get("data-motion-id") for t, a in tags if "pf-motion-demo" in a.get("class", "")}
    assert ids == {"motion-pattern.press-scale-97", "motion-pattern.hover-tint", "motion-pattern.enter-fade-up-8", "motion-pattern.page-crossfade-vt", "motion-pattern.exit-fade-fast"}
    html = (d / "A/tile.html").read_text(encoding="utf-8")
    assert "240ms" in html and "cubic-bezier(0.23, 1, 0.32, 1)" in html


def test_controls_and_font_notice(out):
    d, _ = out
    tags = _parse(d / "A/tile.html")
    for ctl in ["palette", "pairing", "radius", "density", "motion"]:
        assert _count(tags, "select", **{"data-control": ctl}) == 1, ctl
    assert _count(tags, **{"data-control": "theme"}) == 1
    assert _count(tags, "button", **{"data-action": "select"}) >= 1
    assert _count(tags, **{"class": "pf-font-notice", "hidden": None}) == 1
    assert _count(tags, "link", rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Fraunces:wght@600&family=Figtree:wght@400;500;600&family=JetBrains+Mono&display=swap") == 1


def test_tokens_and_variants_css(out):
    d, _ = out
    tokens = (d / "A/tokens.css").read_text(encoding="utf-8")
    assert "--pf-color-bg:" in tokens and "--pf-font-heading:" in tokens and "--pf-dur-base:" in tokens
    variants = (d / "A/variants.css").read_text(encoding="utf-8")
    assert '[data-radius="none"]' in variants and '[data-density="compact"]' in variants and '[data-motion="0"]' in variants
    assert '[data-palette="palette.inline-paper"]' in variants


def test_icons_inlined_from_set(out):
    d, _ = out
    html = (d / "A/tile.html").read_text(encoding="utf-8")
    assert html.count("<svg") >= 12
    assert "Phosphor" in html


def test_preview_chrome_has_no_tells():
    css = (ASSETS / "preview.css").read_text(encoding="utf-8") + (ASSETS / "tile.css").read_text(encoding="utf-8")
    assert "linear-gradient" not in css.lower()
    assert "text-transform: uppercase" not in css.replace(" ", "").lower().replace("text-transform:uppercase", "text-transform: uppercase") or "uppercase" not in css
    assert "→" not in css


def test_build_without_copy_uses_default_copy(out):
    d, report = out
    assert (d / "B/tile.html").exists()
    assert not [w for w in report["warnings"] if "copy" in w.lower()]


def test_render_template_unknown_slot_raises():
    with pytest.raises(KeyError):
        render_template("shell.html", {})


def test_data_json_has_resolved_palettes(out):
    d, _ = out
    data = json.loads((d / "data.json").read_text(encoding="utf-8"))
    assert {x["id"] for x in data["directions"]} == {"A", "B"}
    assert data["directions"][0]["palette_resolved"]["light"]["bg"]["hex"].startswith("#")
    assert data["devices"]


def test_cli(tmp_path):
    assert main(["--directions", str(FIXTURES / "directions_two.json"), "--out", str(tmp_path / "p")]) == 0
    assert (tmp_path / "p" / "index.html").exists()


def test_dark_first_direction_defaults_to_dark_theme(out):
    d, _ = out
    assert 'data-theme="dark"' in (d / "B/tile.html").read_text(encoding="utf-8").split("<head>")[0]
    assert 'data-theme="dark"' not in (d / "A/tile.html").read_text(encoding="utf-8").split("<head>")[0]


def test_direction_id_cannot_escape_out_dir(tmp_path):
    directions = json.load(open(FIXTURES / "directions_two.json", encoding="utf-8"))
    directions["directions"][0]["id"] = "../escaped"
    with pytest.raises(ValueError):
        build(directions, tmp_path / "p", load_graph(), load_devices())
    assert not (tmp_path / "escaped").exists()


def test_vendor_fonts_rewrites_links(tmp_path):
    directions = json.load(open(FIXTURES / "directions_two.json", encoding="utf-8"))
    calls = []

    def fetcher(url, timeout=20):
        calls.append(url)
        if url.endswith(".woff2"):
            return b"wOF2fake"
        return "@font-face{font-family:'Fraunces';src:url(https://fonts.gstatic.com/s/fraunces/v1/abc.woff2) format('woff2');}"

    report = build(directions, tmp_path, load_graph(), load_devices(), vendor_fonts=True, fetcher=fetcher)
    html = (tmp_path / "A/tile.html").read_text(encoding="utf-8")
    assert "fonts.googleapis.com/css2" not in html
    assert 'href="../fonts/' in html
    css_files = list((tmp_path / "fonts").glob("*.css"))
    assert css_files and "url(" in css_files[0].read_text(encoding="utf-8") and "gstatic" not in css_files[0].read_text(encoding="utf-8")
    assert list((tmp_path / "fonts").glob("*.woff2"))
    assert not [w for w in report["warnings"] if "vendoring" in w]


def test_font_notice_uses_fonts_load_result():
    js = (ASSETS / "preview.js").read_text(encoding="utf-8")
    assert "document.fonts.load(" in js and "fonts.check(" not in js


def test_tile_copy_follows_the_brief_not_invoicing(tmp_path):
    directions = json.load(open(FIXTURES / "directions_two.json", encoding="utf-8"))
    directions["brief"]["product"] = "Pawfect, a dog grooming booking site"
    directions["brief"]["words"] = {"name": "Pawfect"}
    for d in directions["directions"]:
        d["copy"] = {"headline": "Grooming that fits your week", "features": [{"title": "Book in a minute", "body": "Pick a slot, pick a groomer."}, {"title": "Reminders that work", "body": "Text the day before."}], "nav": ["Services", "Prices", "About", "Book"]}
    build(directions, tmp_path, load_graph(), load_devices())
    html = (tmp_path / "A/tile.html").read_text(encoding="utf-8")
    assert "Invoice 0142" not in html and "ledgerline" not in html.lower()
    assert "Pawfect" in html and "Reminders that work" in html
