"""Create and verify portable SHA-256 manifests without changing source files."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys


def is_link(path):
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def inventory(root, exclude=None):
    root = Path(root).absolute()
    if is_link(root) or not root.is_dir():
        raise ValueError("Root must be a real directory, not a symlink or junction.")
    files = {}
    for current, dirs, names in os.walk(root, followlinks=False, onerror=lambda err: (_ for _ in ()).throw(err)):
        for name in dirs + names:
            path = Path(current, name)
            if is_link(path):
                raise ValueError(f"Symlink or reparse point is unsupported: {path.relative_to(root).as_posix()}")
        for name in sorted(names):
            path = Path(current, name)
            if exclude is not None and path.resolve() == Path(exclude).resolve():
                continue
            if not path.is_file():
                raise ValueError("Special files are unsupported.")
            files[path.relative_to(root).as_posix()] = path
    return dict(sorted(files.items()))


def fingerprint(path):
    if is_link(path):
        raise ValueError("File changed into a symlink or reparse point.")
    before = path.stat()
    digest = hashlib.sha256()
    count = 0
    with path.open("rb") as stream:
        opened = os.fstat(stream.fileno())
        if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise ValueError("File changed before hashing.")
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            count += len(chunk)
            digest.update(chunk)
        after = os.fstat(stream.fileno())
    final = path.stat()
    signature = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    # Windows stat/fstat may expose different ctime semantics. Compare each API
    # against itself; size/mtime and identity still agree across both APIs.
    if (signature(opened) != signature(after) or signature(before) != signature(final)
            or signature(before)[:4] != signature(opened)[:4] or count != before.st_size):
        raise ValueError("File changed while hashing; stop writers and retry.")
    return {"size": count, "sha256": digest.hexdigest()}


def create(root, manifest):
    manifest = Path(manifest)
    if manifest.exists():
        raise FileExistsError("Manifest exists; choose a new filename.")
    before = inventory(root, manifest)
    records = [{"path": name, **fingerprint(path)} for name, path in before.items()]
    if set(inventory(root, manifest)) != set(before):
        raise ValueError("Directory entries changed during scan; retry on a quiet directory.")
    result = {"format": "handoff-check-v1", "algorithm": "sha256", "files": records}
    with manifest.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, ensure_ascii=True, indent=2)
        stream.write("\n")
    return {"ok": True, "files": len(records), "bytes": sum(r["size"] for r in records)}


def load_manifest(manifest):
    if Path(manifest).stat().st_size > 64 * 1024 * 1024:
        raise ValueError("Manifest exceeds the 64 MiB limit.")
    with Path(manifest).open(encoding="utf-8") as stream:
        data = json.load(stream)
    if not isinstance(data, dict) or data.get("format") != "handoff-check-v1" or data.get("algorithm") != "sha256":
        raise ValueError("Unsupported manifest format or algorithm.")
    if not isinstance(data.get("files"), list):
        raise ValueError("Manifest files must be an array.")
    expected = {}
    for record in data["files"]:
        if not isinstance(record, dict):
            raise ValueError("Invalid file record.")
        name = record.get("path")
        if not isinstance(name, str) or not name or "\\" in name or ":" in name or "\x00" in name:
            raise ValueError("Invalid manifest path.")
        p = PurePosixPath(name)
        if p.is_absolute() or ".." in p.parts or p.as_posix() != name or name == ".":
            raise ValueError("Manifest paths must be normalized relative paths.")
        if name in expected or type(record.get("size")) is not int or record["size"] < 0:
            raise ValueError("Duplicate path or invalid size in manifest.")
        if not isinstance(record.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", record["sha256"]):
            raise ValueError("Invalid SHA-256 in manifest.")
        expected[name] = record
    return expected


def verify(root, manifest):
    expected = load_manifest(manifest)
    actual = inventory(root, manifest)
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    changed = []
    for name in sorted(set(expected) & set(actual)):
        observed = fingerprint(actual[name])
        if any(observed[key] != expected[name][key] for key in ("size", "sha256")):
            changed.append(name)
    if set(inventory(root, manifest)) != set(actual):
        raise ValueError("Directory entries changed during verification.")
    return {"ok": not (missing or extra or changed), "missing": missing, "changed": changed,
            "extra": extra, "checked": len(set(expected) & set(actual))}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["create", "verify"])
    parser.add_argument("directory", type=Path)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args(argv)
    try:
        report = (create if args.command == "create" else verify)(args.directory, args.manifest)
    except (OSError, ValueError, RecursionError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=True))
        return 2
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
