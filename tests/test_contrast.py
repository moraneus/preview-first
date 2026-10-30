import json

import pytest

from contrast import (
    apca_lc,
    best_on_colour,
    grade,
    hex_to_rgb,
    in_gamut,
    main,
    oklch_to_hex,
    parse_oklch,
    rgb_to_hex,
    wcag_ratio,
)


def test_wcag_black_on_white():
    assert round(wcag_ratio("#000000", "#ffffff"), 2) == 21.0


def test_wcag_known_pair():
    assert abs(wcag_ratio("#777777", "#ffffff") - 4.48) < 0.02


def test_apca_known_pairs():
    assert abs(apca_lc("#000000", "#ffffff") - 106.04) < 0.5
    assert abs(apca_lc("#ffffff", "#000000") - (-107.88)) < 0.5
    assert abs(apca_lc("#888888", "#ffffff") - 63.06) < 0.5


def test_oklch_roundtrip_white():
    assert oklch_to_hex(1.0, 0.0, 0.0) == "#ffffff"


def test_oklch_known_colour():
    assert oklch_to_hex(0.6279, 0.2577, 29.23) == "#ff0000"


def test_gamut_mapping_reduces_chroma():
    assert in_gamut(hex_to_rgb(oklch_to_hex(0.7, 0.4, 150)))


def test_grade_roles():
    assert grade("#767676", "#ffffff", "body")["wcag_pass"] is True
    assert grade("#999999", "#ffffff", "body")["ok"] is False
    assert grade("#999999", "#ffffff", "ui")["wcag_pass"] is False
    assert grade("#949494", "#ffffff", "large")["wcag_pass"] is True


def test_best_on_colour():
    assert best_on_colour("#ffeb3b") == "#111111"
    assert best_on_colour("#1d4ed8") == "#ffffff"


def test_parse_oklch():
    assert parse_oklch("oklch(0.5 0.1 200)") == (0.5, 0.1, 200.0)
    assert parse_oklch("oklch(50% 0.1 200deg)") == (0.5, 0.1, 200.0)


def test_hex_roundtrip():
    assert rgb_to_hex(hex_to_rgb("#A1B2C3")) == "#a1b2c3"
    assert rgb_to_hex(hex_to_rgb("#abc")) == "#aabbcc"


def test_cli_prints_grade(capsys):
    assert main(["#111111", "#ffffff", "--role", "body"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is True and out["wcag"] > 15


def test_label_role_thresholds():
    g = grade("#262626", "#b4c0f0", "label")
    assert g["wcag_pass"] is True and g["apca_pass"] is True
