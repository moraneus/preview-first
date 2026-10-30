import json

import pytest

from _common import load_devices
from conftest import ROOT
from validate_graph import validate_against

SCHEMA = json.load(open(ROOT / "skills/preview-first/knowledge/schema.json", encoding="utf-8"))


@pytest.fixture(scope="module")
def devices():
    return load_devices()


def test_device_count_and_vendors(devices):
    assert len(devices) >= 25
    assert {"Apple", "Samsung", "Google"} <= {d["vendor"] for d in devices}


def test_device_fields_and_sanity(devices):
    for d in devices:
        assert validate_against(SCHEMA["files"]["device"], d) == [], d["id"]
        assert 320 <= d["viewport"]["w"] <= 3840, d["id"]
        assert 1 <= d["dpr"] <= 4, d["id"]
        assert d["source"].startswith("http"), d["id"]
        assert d["kind"] in ("phone", "foldable", "tablet", "laptop", "desktop")


def test_fold_devices_have_folded_viewport(devices):
    folds = [d for d in devices if d["kind"] == "foldable"]
    assert folds
    for d in folds:
        assert "folded" in d["fold"] and d["fold"]["crease"] is True


def test_defaults_are_twelve_and_spread(devices):
    defaults = [d for d in devices if d["default"]]
    assert len(defaults) == 12
    assert {d["kind"] for d in defaults} >= {"phone", "foldable", "tablet", "laptop", "desktop"}
    assert {"iphone-17-pro-max", "samsung-galaxy-z-fold7", "google-pixel-10"} <= {d["id"] for d in defaults}


def test_ids_unique_and_ranks_consistent(devices):
    ids = [d["id"] for d in devices]
    assert len(ids) == len(set(ids))
    assert all(isinstance(d["share_rank"], int) and d["share_rank"] >= 1 for d in devices)


def test_island_phones_have_top_inset(devices):
    for d in devices:
        if d["cutout"] == "island":
            assert d["safe_area"]["top"] >= 54, d["id"]
