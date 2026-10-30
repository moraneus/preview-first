"""Shared helpers for preview-first scripts. Standard library only."""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPTS_DIR.parent
KNOWLEDGE_DIR = SKILL_DIR / "knowledge"
ASSETS_DIR = SKILL_DIR / "assets"
VERSION = "0.4.0"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def load_json(path: "str | os.PathLike[str]") -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def dump_json(path: "str | os.PathLike[str]", obj: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME")
    root = Path(base) if base else Path.home() / ".cache"
    return root / "preview-first"


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def today() -> str:
    return _dt.date.today().isoformat()


def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def load_graph(path: "str | os.PathLike[str] | None" = None) -> dict:
    return load_json(path or KNOWLEDGE_DIR / "graph.json")


def load_schema() -> dict:
    return load_json(KNOWLEDGE_DIR / "schema.json")


def load_devices(path: "str | os.PathLike[str] | None" = None) -> list:
    return load_json(path or KNOWLEDGE_DIR / "devices.json")["devices"]


def nodes_by_kind(graph: dict) -> dict:
    out: dict = {}
    for node in graph.get("nodes", []):
        out.setdefault(node["kind"], []).append(node)
    return out


def node_index(graph: dict) -> dict:
    return {n["id"]: n for n in graph.get("nodes", [])}
