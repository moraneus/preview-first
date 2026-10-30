import json

from conftest import FIXTURES, ROOT
from validate_graph import Finding, main, validate, validate_file

MINI = FIXTURES / "mini_graph.json"
SCHEMA = ROOT / "skills" / "preview-first" / "knowledge" / "schema.json"


def _load(p):
    return json.load(open(p))


def _errors():
    return [f for f in validate(_load(MINI), _load(SCHEMA)) if f.level == "error"]


def test_valid_mini_graph_has_only_expected_errors():
    assert {f.node_id for f in _errors()} == {"palette.bad-contrast", "edge:style.a->palette.missing"}


def test_contrast_error_message_names_roles():
    msgs = [f.message for f in _errors() if f.node_id == "palette.bad-contrast"]
    assert any("text on bg" in m for m in msgs)
    assert all("light" in m or "dark" in m for m in msgs)


def test_warnings_for_missing_evidence_and_low_confidence():
    warns = [f for f in validate(_load(MINI), _load(SCHEMA)) if f.level == "warn"]
    assert any(f.node_id == "edge:style.b->type-pairing.p" and "evidence" in f.message for f in warns)
    assert any(f.node_id == "style.b" and "confidence" in f.message for f in warns)


def test_unknown_kind_and_bad_id_are_errors():
    g = _load(MINI)
    g["nodes"].append({"id": "thing.q", "kind": "thing", "name": "Q"})
    g["nodes"].append({"id": "wrong", "kind": "mood", "name": "W", "aliases": [], "source": "x", "added": "2026-01-01", "last_verified": "2026-01-01", "confidence": 1})
    ids = {f.node_id for f in validate(g, _load(SCHEMA)) if f.level == "error"}
    assert {"thing.q", "wrong"} <= ids


def test_duplicate_id_is_error():
    g = _load(MINI)
    g["nodes"].append(dict(g["nodes"][0]))
    assert any(f.node_id == "style.a" and "duplicate" in f.message for f in validate(g, _load(SCHEMA)))


def test_cli_exit_code():
    assert main(["--graph", str(MINI)]) == 1


def test_validate_file_selection():
    schema = _load(SCHEMA)
    assert validate_file({"direction": "A", "overrides": {}, "selected_at": "2026-10-30T00:00:00Z"}, "selection", schema) == []
    assert validate_file({"nope": 1}, "selection", schema)


def test_finding_is_namedtuple():
    f = Finding("error", "x", "m")
    assert f.level == "error" and f.node_id == "x"


def test_validate_file_enforces_direction_id_pattern():
    schema = _load(SCHEMA)
    base = {"version": 1, "brief": {}, "directions": [{"id": "../x", "name": "n", "bundle": {"style": "s", "palette": "p", "type_pairing": "t", "treatments": {}, "motion": [], "icon_set": "i"}}]}
    assert any("pattern" in p for p in validate_file(base, "directions", schema))
    base["directions"][0]["id"] = "A"
    assert validate_file(base, "directions", schema) == []
