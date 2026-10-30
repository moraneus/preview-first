"""Validate the knowledge graph and the JSON files the skill exchanges with Claude.

Usage: validate_graph.py [--graph PATH] [--schema PATH] [--strict]
Exit 1 on any error (or any warning with --strict).
"""
from __future__ import annotations

import argparse
import collections
import datetime as _dt
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _common  # noqa: E402
from contrast import grade, parse_oklch, to_hex  # noqa: E402

Finding = collections.namedtuple("Finding", "level node_id message")

_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ---------------------------------------------------------------- mini JSON schema

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
}


def validate_against(spec: Dict[str, Any], obj: Any, path: str = "$") -> List[str]:
    """Check ``obj`` against a small JSON Schema subset (type, required, properties, items, enum)."""
    problems: List[str] = []
    t = spec.get("type")
    if t:
        py = _TYPES[t]
        if t == "integer" and isinstance(obj, bool):
            problems.append("%s: expected integer, got boolean" % path)
            return problems
        if not isinstance(obj, py):
            problems.append("%s: expected %s, got %s" % (path, t, type(obj).__name__))
            return problems
    if "enum" in spec and obj not in spec["enum"]:
        problems.append("%s: %r not in %s" % (path, obj, spec["enum"]))
    if "pattern" in spec and isinstance(obj, str) and not re.fullmatch(spec["pattern"], obj):
        problems.append("%s: %r does not match pattern %s" % (path, obj, spec["pattern"]))
    if isinstance(obj, dict):
        for key in spec.get("required", []):
            if key not in obj:
                problems.append("%s: missing required key %r" % (path, key))
        for key, sub in spec.get("properties", {}).items():
            if key in obj:
                problems.extend(validate_against(sub, obj[key], "%s.%s" % (path, key)))
    if isinstance(obj, list) and "items" in spec:
        for i, item in enumerate(obj):
            problems.extend(validate_against(spec["items"], item, "%s[%d]" % (path, i)))
    return problems


def validate_file(obj: Any, kind: str, schema: Dict[str, Any]) -> List[str]:
    """Validate a brief / directions / selection / device object. Returns problem strings."""
    return validate_against(schema["files"][kind], obj)


# ---------------------------------------------------------------- graph validation

def _check_palette(node: Dict[str, Any], schema: Dict[str, Any], out: List[Finding]) -> None:
    roles = schema["palette_roles"]
    for mode in ("light", "dark"):
        table = node.get(mode)
        if not isinstance(table, dict):
            out.append(Finding("error", node["id"], "%s: palette mode missing" % mode))
            continue
        hexes: Dict[str, str] = {}
        for role in roles:
            value = table.get(role)
            if value is None:
                out.append(Finding("error", node["id"], "%s: missing role %s" % (mode, role)))
                continue
            try:
                parse_oklch(value) if not str(value).startswith("#") else None
                hexes[role] = to_hex(value)
            except ValueError as exc:
                out.append(Finding("error", node["id"], "%s.%s: %s" % (mode, role, exc)))
        for check in schema["palette_checks"]:
            fg, bg = hexes.get(check["fg"]), hexes.get(check["bg"])
            if not fg or not bg:
                continue
            g = grade(fg, bg, check["role"])
            if not g["ok"]:
                out.append(
                    Finding(
                        "error",
                        node["id"],
                        "%s: %s on %s fails %s (wcag %.2f, apca %.0f)"
                        % (mode, check["fg"], check["bg"], check["role"], g["wcag"], g["apca"]),
                    )
                )


def _check_pairing(node: Dict[str, Any], kspec: Dict[str, Any], out: List[Finding]) -> None:
    enums = kspec.get("enums", {})
    for face_key in ("heading", "body", "mono"):
        face = node.get(face_key)
        if face is None:
            if face_key != "mono":
                out.append(Finding("error", node["id"], "missing face %s" % face_key))
            continue
        for req in kspec.get("face_required", []):
            if req not in face:
                out.append(Finding("error", node["id"], "%s: missing %s" % (face_key, req)))
        for fld in ("category", "source"):
            allowed = enums.get("face." + fld)
            if allowed and face.get(fld) not in allowed:
                out.append(Finding("error", node["id"], "%s.%s: %r not in %s" % (face_key, fld, face.get(fld), allowed)))


def validate(graph: Dict[str, Any], schema: Dict[str, Any], strict: bool = False) -> List[Finding]:
    out: List[Finding] = []
    kinds = schema["node_kinds"]
    id_re = re.compile(schema["id_pattern"])
    seen: Dict[str, int] = {}
    nodes = graph.get("nodes", [])
    today = _dt.date.today()

    for node in nodes:
        nid = str(node.get("id", "<no id>"))
        kind = node.get("kind")
        if nid in seen:
            out.append(Finding("error", nid, "duplicate id"))
            continue
        seen[nid] = 1
        if kind not in kinds:
            out.append(Finding("error", nid, "unknown kind %r" % kind))
            continue
        if not id_re.match(nid) or not nid.startswith(kind + "."):
            out.append(Finding("error", nid, "id must look like '%s.<slug>'" % kind))
        kspec = kinds[kind]
        for req in schema["common_required"] + kspec.get("required", []):
            if req not in node:
                out.append(Finding("error", nid, "missing required field %r" % req))
        for fld, allowed in kspec.get("enums", {}).items():
            if "." in fld:
                continue
            if fld in node and node[fld] not in allowed:
                out.append(Finding("error", nid, "%s: %r not in %s" % (fld, node[fld], allowed)))
        if kind == "treatment":
            axis_values = kspec["axis_values"]
            if node.get("axis") not in axis_values:
                out.append(Finding("error", nid, "unknown axis %r" % node.get("axis")))
            elif node.get("value") not in axis_values[node["axis"]]:
                out.append(Finding("error", nid, "value %r not allowed for axis %s" % (node.get("value"), node["axis"])))
        if kind == "palette" and "light" in node and "dark" in node:
            _check_palette(node, schema, out)
        if kind == "type-pairing":
            _check_pairing(node, kspec, out)
        if kind == "idea":
            hook = node.get("renders")
            if hook is not None and hook not in kspec.get("render_hooks", []):
                out.append(Finding("error", nid, "renders %r is not a known render hook" % hook))
            if not isinstance(node.get("seen_on"), list) or not node.get("seen_on"):
                out.append(Finding("error", nid, "seen_on must list at least one URL"))
        if kind == "style":
            for iid in node.get("ideas", []) or []:
                if not str(iid).startswith("idea."):
                    out.append(Finding("error", nid, "ideas entries must be idea ids, got %r" % iid))
        conf = node.get("confidence")
        if isinstance(conf, (int, float)):
            if not 0 <= conf <= 1:
                out.append(Finding("error", nid, "confidence outside 0..1"))
            elif conf < 0.6:
                out.append(Finding("warn", nid, "low confidence %.2f" % conf))
        for date_field in ("added", "last_verified"):
            val = node.get(date_field)
            if val is not None and not _ISO.match(str(val)):
                out.append(Finding("error", nid, "%s is not an ISO date" % date_field))
        lv = node.get("last_verified")
        if lv and _ISO.match(str(lv)):
            age = (today - _dt.date.fromisoformat(lv)).days
            if age > 365:
                out.append(Finding("warn", nid, "last_verified is %d days old" % age))

    for node in nodes:
        if node.get("kind") == "style":
            for iid in node.get("ideas", []) or []:
                if iid not in seen:
                    out.append(Finding("error", node["id"], "ideas references missing node %r" % iid))
    ref_ids = {n["id"] for n in nodes if n.get("kind") == "reference-site"}
    evidence_expected = set(schema.get("edge_evidence_expected", []))
    for edge in graph.get("edges", []):
        eid = "edge:%s->%s" % (edge.get("from"), edge.get("to"))
        if edge.get("kind") not in schema["edge_kinds"]:
            out.append(Finding("error", eid, "unknown edge kind %r" % edge.get("kind")))
        for end in ("from", "to"):
            if edge.get(end) not in seen:
                out.append(Finding("error", eid, "dangling %s endpoint %r" % (end, edge.get(end))))
        w = edge.get("weight", 1.0)
        if not isinstance(w, (int, float)) or not 0 <= w <= 1:
            out.append(Finding("error", eid, "weight must be 0..1"))
        ev = edge.get("evidence", [])
        for e in ev:
            if e not in ref_ids:
                out.append(Finding("error", eid, "evidence %r is not a reference-site" % e))
        if edge.get("kind") in evidence_expected and not ev:
            out.append(Finding("warn", eid, "no evidence on %s edge" % edge.get("kind")))

    return out


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate the preview-first knowledge graph.")
    ap.add_argument("--graph", default=str(_common.KNOWLEDGE_DIR / "graph.json"))
    ap.add_argument("--schema", default=str(_common.KNOWLEDGE_DIR / "schema.json"))
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--quiet", action="store_true")
    ns = ap.parse_args(list(argv))
    findings = validate(_common.load_json(ns.graph), _common.load_json(ns.schema), ns.strict)
    errors = [f for f in findings if f.level == "error"]
    warns = [f for f in findings if f.level == "warn"]
    if not ns.quiet:
        for f in findings:
            print("%-5s %s: %s" % (f.level.upper(), f.node_id, f.message))
        print("%d error(s), %d warning(s)" % (len(errors), len(warns)))
    if errors or (ns.strict and warns):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
