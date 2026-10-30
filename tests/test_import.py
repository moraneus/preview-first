import json

import pytest

from _common import load_devices, load_graph
from build_preview import build
from conftest import FIXTURES
from import_direction import from_css, from_dtcg, from_tailwind_config, from_url, main, to_direction


@pytest.fixture(scope="module")
def graph():
    return load_graph()


def test_from_css_extracts_colours_fonts_radius():
    obs = from_css((FIXTURES / "site.css").read_text(encoding="utf-8"))
    assert obs["colors"][0] == "#58a6ff"  # most frequent
    assert "#0b0f14" in obs["colors"] and "#e6edf3" in obs["colors"]
    assert obs["fonts"][:2] == ["Geist", "Space Grotesk"] or set(obs["fonts"][:2]) == {"Geist", "Space Grotesk"}
    assert 8 in obs["radius"] and 12 in obs["radius"]


def test_from_tailwind_config():
    obs = from_tailwind_config((FIXTURES / "tailwind.config.js").read_text(encoding="utf-8"))
    assert {"#0f766e", "#111827", "#f9fafb"} <= set(obs["colors"])
    assert "Manrope" in obs["fonts"] and "Fraunces" in obs["fonts"]
    assert 12 in obs["radius"]


def test_from_dtcg():
    obs = from_dtcg(json.load(open(FIXTURES / "tokens_dtcg.json", encoding="utf-8")))
    assert obs["colors"][:2] == ["#fbfaf7", "#1f1d1a"]
    assert obs["fonts"] == ["Newsreader", "Inter Tight"]
    assert obs["radius"] == [6]


def test_from_url_ignores_cross_origin_styles():
    html = ('<html><head><link rel="stylesheet" href="/site.css"><link rel="stylesheet" href="https://cdn.example/other.css">'
            '<style>body{color:#123456}</style></head><body style="background:#abcdef">x</body></html>')
    fetched = []

    def fetcher(url, timeout=15):
        fetched.append(url)
        if url.endswith("/site.css"):
            return (FIXTURES / "site.css").read_text(encoding="utf-8")
        if url.endswith("other.css"):
            return "body{color:#ff0000}"
        return html

    obs = from_url("https://example.com/", fetcher=fetcher)
    assert "#123456" in obs["colors"] and "#abcdef" in obs["colors"] and "#58a6ff" in obs["colors"]
    assert "#ff0000" not in obs["colors"]
    assert not any("cdn.example" in u for u in fetched)


def test_to_direction_light_look_builds(graph, tmp_path):
    obs = from_dtcg(json.load(open(FIXTURES / "tokens_dtcg.json", encoding="utf-8")))
    d = to_direction(obs, graph, id="X", name="Current look")
    assert d["id"] == "X" and d["bundle"]["style"].startswith("style.")
    assert isinstance(d["bundle"]["palette"], dict) and d["bundle"]["palette"]["scheme"] in ("light", "both")
    assert d["bundle"]["type_pairing"]["heading"]["family"] == "Newsreader"
    assert d["bundle"]["style"] == "style.paper-editorial"
    directions = {"version": 1, "brief": {"product": "Test", "product_type": "product-type.saas", "page_type": "marketing"}, "directions": [d]}
    report = build(directions, tmp_path, graph, load_devices())
    assert (tmp_path / "X/tile.html").exists()


def test_to_direction_dark_look_picks_dark_style(graph):
    obs = from_css((FIXTURES / "site.css").read_text(encoding="utf-8"))
    d = to_direction(obs, graph)
    assert d["bundle"]["style"] == "style.dark-console"
    assert d["bundle"]["palette"]["scheme"] == "dark"
    assert d["bundle"]["type_pairing"]["body"]["family"] == "Geist"


def test_cli_appends_to_directions(tmp_path):
    directions = tmp_path / "directions.json"
    directions.write_text(json.dumps(json.load(open(FIXTURES / "directions_two.json", encoding="utf-8"))))
    assert main(["--css", str(FIXTURES / "site.css"), "--into", str(directions), "--name", "Today"]) == 0
    out = json.load(open(directions, encoding="utf-8"))
    assert [d["id"] for d in out["directions"]] == ["A", "B", "C"] and out["directions"][2]["name"] == "Today"


def test_hostile_font_names_are_dropped():
    css = "body{font-family:\"Evil'; } body{background:red} x{\", Geist}"
    obs = from_css(css)
    assert obs["fonts"] == ["Geist"]
    obs = from_dtcg({"font": {"body": {"$type": "fontFamily", "$value": ["Bad</style><script>", "Figtree"]}}})
    assert obs["fonts"] == []  # only the first entry is considered, and it is rejected
