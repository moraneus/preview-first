import json

from conftest import ROOT


def test_plugin_and_marketplace_names_match():
    plugin = json.load(open(ROOT / ".claude-plugin" / "plugin.json"))
    market = json.load(open(ROOT / ".claude-plugin" / "marketplace.json"))
    assert plugin["name"] == "preview-first"
    assert market["name"] == "preview-first"
    assert market["plugins"][0]["name"] == "preview-first"
    assert market["plugins"][0]["source"] == "./"
    assert plugin["license"] == "MIT"


def test_skill_frontmatter_portable_keys_only():
    text = (ROOT / "skills" / "preview-first" / "SKILL.md").read_text()
    assert text.startswith("---\n")
    fm = text.split("---")[1]
    keys = {
        line.split(":")[0].strip()
        for line in fm.strip().splitlines()
        if ":" in line and not line.startswith(" ")
    }
    assert keys <= {"name", "description", "license", "metadata"}
    assert "name: preview-first" in fm


def test_common_cache_dir_respects_xdg(monkeypatch, tmp_path, scripts_path):
    import _common

    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    assert _common.cache_dir() == tmp_path / "preview-first"


def test_common_slugify():
    import _common

    assert _common.slugify("Paper & Ink, 2026!") == "paper-ink-2026"
