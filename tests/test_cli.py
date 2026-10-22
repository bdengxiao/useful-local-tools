from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("tool", ["csv", "handoff", "env"])
def test_cli_help(tool):
    result = subprocess.run([sys.executable, str(ROOT / "run.py"), tool, "--help"], capture_output=True)
    assert result.returncode == 0
    assert b"usage:" in result.stdout


def test_env_cli_failure_and_success():
    common = [sys.executable, str(ROOT / "run.py"), "env", "--example", str(ROOT / "examples/config/.env.example")]
    failed = subprocess.run(common + ["--env", str(ROOT / "examples/config/local.sample")], capture_output=True)
    passed = subprocess.run(common + ["--env", str(ROOT / "examples/config/ready.sample")], capture_output=True)
    assert failed.returncode == 1
    assert passed.returncode == 0
    assert b"synthetic-demo-only" not in passed.stdout + passed.stderr


def test_handoff_cli_difference_exit(tmp_path):
    root = tmp_path / "folder"
    root.mkdir()
    (root / "a.txt").write_text("before")
    manifest = tmp_path / "manifest.json"
    command = [sys.executable, str(ROOT / "run.py"), "handoff"]
    created = subprocess.run(command + ["create", str(root), str(manifest)], capture_output=True)
    assert created.returncode == 0
    (root / "a.txt").write_text("after")
    checked = subprocess.run(command + ["verify", str(root), str(manifest)], capture_output=True)
    assert checked.returncode == 1
    assert b'"a.txt"' in checked.stdout


def test_csv_cli_success(tmp_path):
    result = subprocess.run([sys.executable, str(ROOT / "run.py"), "csv", str(ROOT / "examples/orders.csv"),
                             str(tmp_path / "orders.xlsx")], capture_output=True)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "orders.xlsx").is_file()
