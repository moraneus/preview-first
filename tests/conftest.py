import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "preview-first" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


@pytest.fixture(scope="session", autouse=True)
def scripts_path():
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    return SCRIPTS


@pytest.fixture
def tmp_project(tmp_path):
    (tmp_path / ".git").mkdir()
    return tmp_path
