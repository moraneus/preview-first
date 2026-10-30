import json
import re

import pytest

from _common import load_devices, load_graph
from conftest import FIXTURES
from export_design import GEN_END, GEN_START, export, main

SELECTION = {"direction": "A", "overrides": {"palette": "palette.inline-paper", "radius": "sm", "theme": "light"}, "selected_at": "2026-10-30T10:00:00Z"}


@pytest.fixture
def directions():
    return json.load(open(FIXTURES / "directions_two.json"))


def _export(project, directions, selection=SELECTION):
    return export(selection, directions, project, load_graph(), load_devices())


def test_fresh_export_writes_contract_and_tokens(tmp_project, directions):
    report = _export(tmp_project, directions)
    design = tmp_project / "design"
    for name in ("DESIGN.md", "tokens.json", "tokens.css"):
        assert (design / name).exists(), name
    md = (design / "DESIGN.md").read_text()
    assert GEN_START in md and GEN_END in md
    for heading in ("## Identity", "## Palette", "## Typography", "## Spacing and radius", "## Elevation", "## Layout", "## Components",
                    "## Motion", "## Iconography", "## Imagery", "## Writing style", "## Accessibility floor", "## Device checks", "## Do not", "## Project notes"):
        assert heading in md, heading
    assert "Ledger" in md and "Fraunces" in md and "#154d8c" in md
    assert report["history"] is None and report["claude_md_updated"] is True


def test_tokens_json_is_dtcg(tmp_project, directions):
    _export(tmp_project, directions)
    tokens = json.load(open(tmp_project / "design" / "tokens.json"))
    assert set(tokens) >= {"color", "font", "size", "radius", "space", "duration", "easing"}

    def leaves(node):
        if isinstance(node, dict) and "$value" in node:
            yield node
        elif isinstance(node, dict):
            for v in node.values():
                yield from leaves(v)

    found = list(leaves(tokens))
    assert found and all("$type" in leaf for leaf in found)
    assert tokens["color"]["light"]["bg"]["$value"].startswith("#")
    assert tokens["color"]["dark"]["bg"]["$value"].startswith("#")


def test_tokens_css_has_modes_and_motion(tmp_project, directions):
    _export(tmp_project, directions)
    css = (tmp_project / "design" / "tokens.css").read_text()
    assert "--pf-color-bg:" in css and '[data-theme="dark"]' in css and "--pf-dur-base:" in css and "--pf-font-heading:" in css


def test_tailwind_only_when_detected(tmp_project, directions):
    _export(tmp_project, directions)
    assert not (tmp_project / "design" / "tailwind.css").exists()
    (tmp_project / "app.css").write_text('@import "tailwindcss";\n')
    _export(tmp_project, directions)
    tw = (tmp_project / "design" / "tailwind.css").read_text()
    assert "@theme" in tw and "--color-primary:" in tw and "--font-heading:" in tw


def test_reexport_preserves_project_notes_and_keeps_history(tmp_project, directions):
    _export(tmp_project, directions)
    md_path = tmp_project / "design" / "DESIGN.md"
    md = md_path.read_text()
    md = md.replace("## Project notes\n", "## Project notes\n\nKeep the invoice table dense; finance users asked for it.\n")
    md_path.write_text(md)
    selection = dict(SELECTION, overrides={"radius": "lg"})
    report = _export(tmp_project, directions, selection)
    new = md_path.read_text()
    assert "Keep the invoice table dense; finance users asked for it." in new
    assert "Radius scale: **lg**" in new
    assert report["history"] and (tmp_project / "design" / "history").exists()
    assert any(p.name == "DESIGN.md" for p in (tmp_project / "design" / "history").rglob("*"))


def test_claude_md_pointer_is_idempotent(tmp_project, directions):
    _export(tmp_project, directions)
    _export(tmp_project, directions)
    text = (tmp_project / "CLAUDE.md").read_text()
    assert text.count("design/DESIGN.md") == 1
    assert ".design-preview/" in (tmp_project / ".gitignore").read_text()


def test_overrides_change_palette_and_pairing(tmp_project, directions):
    directions["directions"][0]["bundle"]["alternatives"]["palettes"] = ["palette.paper-ink"]
    directions["directions"][0]["bundle"]["alternatives"]["type_pairings"] = ["type-pairing.geist-geist"]
    selection = dict(SELECTION, overrides={"palette": "palette.paper-ink", "pairing": "type-pairing.geist-geist", "motion": "2"})
    _export(tmp_project, directions, selection)
    md = (tmp_project / "design" / "DESIGN.md").read_text()
    assert "Paper & Ink" in md and "Geist" in md and "Motion level: **2**" in md


def test_unknown_direction_raises(tmp_project, directions):
    with pytest.raises(KeyError):
        _export(tmp_project, directions, {"direction": "Z", "overrides": {}})


def test_cli(tmp_project, directions, tmp_path):
    sel = tmp_path / "selection.json"
    sel.write_text(json.dumps(SELECTION))
    assert main(["--selection", str(sel), "--directions", str(FIXTURES / "directions_two.json"), "--project", str(tmp_project)]) == 0
    assert (tmp_project / "design" / "DESIGN.md").exists()


def test_reexport_keeps_text_above_markers_and_unmarked_files(tmp_project, directions):
    _export(tmp_project, directions)
    md_path = tmp_project / "design" / "DESIGN.md"
    md_path.write_text("Top note kept.\n\n" + md_path.read_text())
    _export(tmp_project, directions)
    assert md_path.read_text().startswith("Top note kept.")
    # a hand-written file with no markers is preserved as free text
    md_path.write_text("# My own contract\n\nHand written, no markers.\n")
    _export(tmp_project, directions)
    new = md_path.read_text()
    assert GEN_START in new and "Hand written, no markers." in new


def test_history_never_overwrites(tmp_project, directions):
    reports = [_export(tmp_project, directions) for _ in range(4)]
    hist = {r["history"] for r in reports if r["history"]}
    assert len(hist) == 3
    assert all((tmp_project / "design" / "history").exists() for _ in hist)


def test_tailwind_v3_gets_note_not_theme(tmp_project, directions):
    (tmp_project / "tailwind.config.js").write_text("module.exports = {}")
    (tmp_project / "package.json").write_text(json.dumps({"devDependencies": {"tailwindcss": "^3.4.0"}}))
    _export(tmp_project, directions)
    assert not (tmp_project / "design" / "tailwind.css").exists()
    assert (tmp_project / "design" / "tailwind.md").exists()
    (tmp_project / "package.json").write_text(json.dumps({"devDependencies": {"tailwindcss": "^4.1.0"}}))
    _export(tmp_project, directions)
    tw = (tmp_project / "design" / "tailwind.css").read_text()
    assert tw.index('@import "tailwindcss"') < tw.index("@theme") and tw.index('@import "./tokens.css"') < tw.index("@theme")
    assert "@theme inline" in tw
