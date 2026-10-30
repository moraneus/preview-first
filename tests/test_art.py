import re
from xml.etree import ElementTree as ET

import pytest

from drafts import art

KINDS = ["ui_mock", "terminal", "blueprint", "isometric", "swiss", "contours", "halftone", "orbit", "stickers", "sparklines", "mark", "glass", "figure"]


@pytest.mark.parametrize("kind", KINDS)
def test_every_kind_renders_valid_svg_using_palette_vars(kind):
    svg = art.render(kind, seed="A", label="Fig 0.1")
    assert svg.startswith("<svg") and svg.rstrip().endswith("</svg>")
    ET.fromstring(svg)  # well formed
    assert "var(--pf-color-" in svg or "currentColor" in svg
    assert 'aria-hidden="true"' in svg or "<title>" in svg
    assert "linear-gradient" not in svg and "#8b5cf6" not in svg.lower()


def test_art_is_deterministic_per_seed():
    assert art.render("contours", seed="A") == art.render("contours", seed="A")
    assert art.render("contours", seed="A") != art.render("contours", seed="B")


def test_unknown_kind_falls_back():
    assert art.render("nope", seed="A").startswith("<svg")


def test_every_style_declares_art():
    from _common import load_graph, nodes_by_kind
    for s in nodes_by_kind(load_graph())["style"]:
        assert s.get("art", {}).get("hero") in KINDS, s["id"]
        assert s.get("art", {}).get("feature") in KINDS, s["id"]
        assert s.get("conventionality") in ("familiar", "distinct"), s["id"]
