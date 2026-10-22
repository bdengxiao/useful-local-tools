# Validation record

Date: 2026-10-22. Release scope: initial working CLI/Skill version.

## Local verification

- Windows, CPython 3.12.14, openpyxl 3.1.5, pytest 9.1.1.
- `python -m pytest tests -q --basetemp=<fresh workspace temp directory>`: **45 passed, 1 skipped**.
- The skipped test attempts to create a symbolic link; this Windows account lacks that privilege. Link rejection is implemented, but that local case is not verified. CI includes Linux and macOS where the same test should execute; consult actual Actions results.
- All three `SKILL.md` files passed the skill-creator frontmatter/name/scaffold validator.
- Actual subprocess tests exercised all three CLI help pages, CSV conversion, handoff mismatch exit status and dotenv pass/fail exit statuses.
- CSV was reopened with openpyxl and its XLSX XML inspected: leading zeros, long IDs, Chinese/emoji, quoted delimiters, embedded newlines, whitespace and formula-like strings retain text values; no formula XML or external links were emitted. Empty strings become blank cells.
- Corrupt/unsupported CSV inputs were rejected without a published output. Tests checked that source files and existing output files remain unchanged.
- Directory tests cover a real copy, missing/extra files, same-size content changes, invalid/duplicate manifest records and a simulated file change during hashing.
- Dotenv tests cover values omitted from diagnostics, malformed input, encoding errors, duplicates, optional empty keys, extra keys and interpolation reported without evaluation.

## Fixed during verification

Windows `stat` and `fstat` can expose different ctime values on copied files. The implementation compares each API against itself and compares identity/size/mtime across the APIs, avoiding false positives while retaining content hashing and change checks. A real copy/verify test covers this case.

## What this does not prove

No desktop Excel/WPS round trip, hostile concurrent filesystem attack, production-scale benchmark, external credential validation, user interview, willingness-to-pay study or market-size estimate was performed. File scans require a quiet source and are not atomic snapshots. Multi-platform CI configuration is not itself proof that remote CI passed. The current GitHub Actions run is the source of truth for remote results.
