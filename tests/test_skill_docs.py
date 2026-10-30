import json
import re

from conftest import ROOT

SKILL = ROOT / "skills/preview-first"
REFS = ["process", "color", "typography", "motion", "components", "layout", "anti-patterns", "devices", "handoff", "platform"]


def _skill_text():
    return (SKILL / "SKILL.md").read_text()


def test_skill_md_length_and_frontmatter():
    text = _skill_text()
    assert len(text.splitlines()) < 500
    fm = text.split("---")[1]
    desc = re.search(r"^description:\s*(.+)$", fm, re.M).group(1)
    assert len(desc) <= 1024
    for word in ("preview", "design", "before"):
        assert word in desc.lower()


def test_every_script_is_mentioned():
    text = _skill_text()
    for script in sorted(p.name for p in (SKILL / "scripts").glob("*.py") if not p.name.startswith("_")):
        assert script in text, script


def test_every_reference_exists_and_is_linked():
    text = _skill_text()
    for ref in REFS:
        path = SKILL / "references" / ("%s.md" % ref)
        assert path.exists(), ref
        assert "references/%s.md" % ref in text, ref
        assert 60 <= len(path.read_text().splitlines()) <= 600, ref


def test_components_reference_lists_every_treatment():
    text = (SKILL / "references" / "components.md").read_text()
    schema = json.load(open(SKILL / "knowledge" / "schema.json"))
    for axis, values in schema["node_kinds"]["treatment"]["axis_values"].items():
        assert axis in text, axis
        for v in values:
            assert re.search(r"\b%s\b" % re.escape(v), text), (axis, v)


def test_skill_names_the_flow_and_the_wait():
    text = _skill_text()
    for phrase in ("brief.json", "directions.json", "selection.json", "design/DESIGN.md", "--open", "wait"):
        assert phrase in text, phrase


def test_docs_have_no_tells():
    for path in [SKILL / "SKILL.md"] + [SKILL / "references" / ("%s.md" % r) for r in REFS]:
        text = path.read_text()
        assert "—" not in text, path.name
        assert not re.search("[\U0001F300-\U0001FAFF]", text), path.name


def test_anti_patterns_cover_known_tells():
    text = (SKILL / "references" / "anti-patterns.md").read_text().lower()
    for tell in ("purple", "inter", "emoji", "eyebrow", "lorem", "gradient", "three", "arrow"):
        assert tell in text, tell
