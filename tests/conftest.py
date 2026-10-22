import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    path = ROOT / "skills" / name / "scripts" / (name.replace("-", "_") + ".py")
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def csv_tool():
    return load("csv-text-safe")


@pytest.fixture
def handoff():
    return load("handoff-check")


@pytest.fixture
def env_tool():
    return load("env-preflight")
