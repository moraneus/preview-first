import json

import pytest

from conftest import FIXTURES
from palette import ROLES, derive_roles, motion_tokens, resolve_palette, scale_tokens, tokens_css


@pytest.fixture
def pal():
    g = json.load(open(FIXTURES / "mini_graph.json"))
    return next(n for n in g["nodes"] if n["id"] == "palette.good")


@pytest.fixture
def pairing():
    g = json.load(open(FIXTURES / "mini_graph.json"))
    return next(n for n in g["nodes"] if n["id"] == "type-pairing.p")


def test_resolve_renders_hex_for_every_role(pal):
    r = resolve_palette(pal)
    assert set(r["light"]) == set(ROLES) and set(r["dark"]) == set(ROLES)
    assert all(v["hex"].startswith("#") and v["oklch"].startswith("oklch(") for v in r["light"].values())
    assert r["warnings"] == []
    assert all(c["ok"] for c in r["checks"])


def test_brand_override_recomputes_on_primary(pal):
    r = resolve_palette(pal, {"brand_primary": "#ffeb3b"})
    assert r["light"]["primary"]["hex"] == "#ffeb3b"
    assert r["light"]["on_primary"]["hex"] == "#111111"
    assert r["dark"]["primary"]["hex"] == "#ffeb3b"


def test_failing_override_is_warned_not_hidden(pal):
    r = resolve_palette(pal, {"brand_primary": "#fff59d"})
    assert any("primary" in w for w in r["warnings"])
    assert any(not c["ok"] for c in r["checks"])


def test_tokens_css_has_light_and_dark(pal):
    css = tokens_css(resolve_palette(pal))
    assert "--pf-color-bg:" in css
    assert '[data-theme="dark"]' in css
    assert "prefers-color-scheme: dark" in css
    assert "color-scheme: light dark" in css
    assert "--pf-color-primary-oklch:" in css


def test_tokens_css_scoped_selector(pal):
    css = tokens_css(resolve_palette(pal), selector='[data-palette="palette.good"]')
    assert css.count('[data-palette="palette.good"]') >= 2


def test_scale_tokens_ratio(pairing):
    css = scale_tokens("md", "regular", pairing)
    assert "--pf-text-base: 1rem" in css
    assert "--pf-text-xl: 1.25rem" in css
    assert "--pf-text-2xl: 1.563rem" in css
    assert "--pf-font-heading: 'Fraunces', Georgia, serif" in css
    assert "--pf-measure: 66ch" in css
    assert "--pf-radius-md: 0.5rem" in css


def test_radius_scale_none_is_zero(pairing):
    css = scale_tokens("none", "regular", pairing)
    assert "--pf-radius-md: 0;" in css and "--pf-radius-full: 0;" in css


def test_radius_scale_pill(pairing):
    assert "--pf-radius-full: 9999px" in scale_tokens("pill", "regular", pairing)


def test_density_changes_space(pairing):
    airy = scale_tokens("md", "airy", pairing)
    compact = scale_tokens("md", "compact", pairing)
    assert "--pf-space-4: 1.25rem" in airy and "--pf-space-4: 0.75rem" in compact


def test_motion_tokens_levels():
    assert "--pf-dur-fast: 0ms" in motion_tokens(0)
    css = motion_tokens(1)
    assert "--pf-dur-fast: 120ms" in css and "--pf-ease-out:" in css


def test_derive_roles_builds_full_palette():
    roles = derive_roles("#fbfaf7", "#1f1d1a", "#1d4ed8")
    assert set(roles["light"]) == set(ROLES) and set(roles["dark"]) == set(ROLES)
    assert all(v.startswith("oklch(") for v in roles["light"].values())


def test_font_stack_strips_css_breaking_characters(pairing):
    pairing = dict(pairing, heading={"family": "Evil'; } body{background:red} x{", "category": "serif-transitional", "weights": [600], "source": "google"})
    css = scale_tokens("md", "regular", pairing)
    assert "}" not in css.split("--pf-font-heading:")[1].split("\n")[0]
    assert "background:red" not in css.replace(" ", "") or ";" not in css.split("--pf-font-heading:")[1].split("\n")[0][:-1]
