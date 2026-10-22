import json
from pathlib import Path
import shutil

import pytest


def payload(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    (root / "子目录").mkdir()
    (root / "子目录" / "data.txt").write_text("内容", encoding="utf-8")
    (root / "empty.bin").write_bytes(b"")
    return root


def test_portable_manifest_and_drift(tmp_path, handoff):
    root = payload(tmp_path)
    manifest = root / "manifest.json"
    assert handoff.create(root, manifest)["files"] == 2
    destination = tmp_path / "copy"
    shutil.copytree(root, destination)
    copied_manifest = destination / "manifest.json"
    assert handoff.verify(destination, copied_manifest)["ok"]
    (destination / "empty.bin").unlink()
    (destination / "子目录" / "data.txt").write_text("changed")
    (destination / "extra.txt").write_text("new")
    report = handoff.verify(destination, copied_manifest)
    assert report["missing"] == ["empty.bin"]
    assert report["changed"] == ["子目录/data.txt"]
    assert report["extra"] == ["extra.txt"]
    assert not report["ok"]
    assert (root / "empty.bin").exists()


def test_same_size_change_detected(tmp_path, handoff):
    root = payload(tmp_path)
    file = root / "a.txt"
    file.write_bytes(b"abcd")
    manifest = tmp_path / "manifest.json"
    handoff.create(root, manifest)
    file.write_bytes(b"abce")
    assert handoff.verify(root, manifest)["changed"] == ["a.txt"]


@pytest.mark.parametrize("name", ["../outside", "/absolute", "C:/windows", "a\\b", "./a", "a//b", "a/../b", ".", ""])
def test_untrusted_paths_rejected(tmp_path, handoff, name):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"format": "handoff-check-v1", "algorithm": "sha256", "files": [
        {"path": name, "size": 1, "sha256": "a" * 64}]}))
    with pytest.raises(ValueError):
        handoff.verify(tmp_path, manifest)


def test_manifest_validation_and_no_overwrite(tmp_path, handoff):
    root = payload(tmp_path)
    manifest = tmp_path / "manifest.json"
    handoff.create(root, manifest)
    before = manifest.read_bytes()
    with pytest.raises(FileExistsError):
        handoff.create(root, manifest)
    assert manifest.read_bytes() == before
    data = json.loads(before)
    data["files"].append(data["files"][0])
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        handoff.load_manifest(manifest)


def test_links_rejected(tmp_path, handoff):
    root = payload(tmp_path)
    link = root / "linked"
    try:
        link.symlink_to(tmp_path, target_is_directory=True)
    except OSError:
        pytest.skip("OS account cannot create symlinks")
    with pytest.raises(ValueError):
        handoff.create(root, tmp_path / "manifest.json")


def test_changed_during_hash_is_error(tmp_path, handoff, monkeypatch):
    root = payload(tmp_path)
    file = root / "empty.bin"
    original = Path.stat
    count = 0

    def changing_stat(self, *args, **kwargs):
        nonlocal count
        if self == file and kwargs.get("follow_symlinks", True):
            count += 1
            if count == 2:
                self.write_bytes(b"changed")
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", changing_stat)
    with pytest.raises(ValueError, match="changed"):
        handoff.fingerprint(file)
