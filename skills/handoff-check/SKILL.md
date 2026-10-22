---
name: handoff-check
description: Create or verify a portable SHA-256 file manifest for a folder handoff or copy, reporting missing, changed and extra files without modifying source data.
---

Use Python 3.10+; no third-party packages are needed. Resolve `scripts/handoff_check.py` relative to this skill folder.

```sh
python scripts/handoff_check.py create /path/to/folder /path/to/manifest.json
python scripts/handoff_check.py verify /path/to/copied-folder /path/to/manifest.json
```

Use a quiet directory and a new manifest path. The manifest may be inside the source directory; the exact manifest path is excluded from the scan. Keep its relative location unchanged when copying the folder. Source files are read only. All regular files, including dotfiles, are covered; there are no implicit ignore rules. Empty directories and file metadata are not covered. Links and Windows reparse points are refused, including a root that is itself a link.

Interpret exit codes: 0 means the operation passed; 1 means verification found differences; 2 means the scan or manifest could not be trusted. Report the `missing`, `changed` and `extra` lists separately. Do not respond to differences by deleting, copying or repairing files without a user request covering that action.

The check is a sequential comparison, not an atomic snapshot, a backup or an authenticity signature. Active writers can invalidate results after a file is read. Ask the user to stop writers or use a filesystem snapshot when that matters. A matching result does not prove that an application can open the files. A hostile process changing links during the scan is outside the threat model. Manifest names reveal directory structure; keep the manifest local unless sharing it is requested.
