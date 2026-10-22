# Useful Local Tools

Three focused Python CLIs with optional self-contained AI skills. Local processing, no API keys, no telemetry. Python 3.10+, MIT license. [中文文档](README.md).

| Tool | Purpose | Dependencies |
| --- | --- | --- |
| CSV Text Safe | CSV/TSV to XLSX with every cell stored as literal text | openpyxl >=3.1.5,<4 |
| Handoff Check | Portable SHA-256 manifests; missing/changed/extra reports | Standard library |
| Env Preflight | Compare dotenv keys without printing secret values | Standard library |

```sh
git clone https://github.com/bdengxiao/useful-local-tools.git
cd useful-local-tools
python -m pip install -r requirements.txt
python run.py csv examples/orders.csv orders-text.xlsx
python run.py handoff create examples/handoff manifest.json
python run.py handoff verify examples/handoff manifest.json
python run.py env --example examples/config/.env.example --env examples/config/ready.sample
```

Use `python run.py <tool> --help` for options. Existing outputs are never overwritten. Only the CSV tool requires installation of third-party dependencies. Each script in `skills/<name>/scripts/` also runs independently.

## Important boundaries

**CSV:** UTF-8/BOM and comma by default; specify `--encoding gb18030` or `--delimiter tab` when appropriate. All fields are text, including dates and numbers. This prevents automatic identifier conversion and stores formula-like values as strings, but is unsuitable for immediate numerical analysis. Empty strings become blank Excel cells. Encoding errors, uneven rows, invalid XML characters and Excel size limits are rejected. No encoding guessing, truncation or recovery of already damaged input. Re-exporting to CSV removes the XLSX typing protection.

**Handoff:** Includes regular files and dotfiles, excludes the exact manifest path, rejects links/reparse points, uses portable relative paths. A manifest inside the payload must retain its relative location after copying. No metadata or empty-directory verification. No deletion or repairs. Run on a quiet directory: a sequential scan is not a filesystem snapshot, backup or authenticity proof. Concurrent hostile link replacement is outside the threat model. Manifests are limited to 64 MiB.

**Env:** Supports UTF-8/BOM, optional `export`, ASCII keys, single-line quoted/unquoted values and comments. Multiline quotes are rejected. Reports keys and line numbers, never values or raw erroneous lines. Does not expand variables, run commands, merge framework layers or validate credentials. `--allow-empty KEY` may be repeated; `--strict-extra` makes extra keys fail. Placeholder detection is heuristic (`changeme`, `replace-me`, `your_*`, `<...>`, `TODO`, etc.). Interpolation-like values appear in `unexpanded` as an informational warning. Key names themselves can be sensitive. Input limit: 4 MiB per file.

Exit status: **0** passed, **1** differences/configuration findings, **2** invalid input or operation error. Output reports are JSON.

## AI skills

Copy a complete folder from `skills/` into your assistant's skill directory. Do not overwrite an existing skill without comparing it. The CSV skill includes its own requirements.txt; the other skills need only Python. Each folder contains its own script and task-specific instructions. The repository root is not required after copying a skill.

## Development

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

CI is configured for Windows/Linux/macOS and Python 3.10/3.12. See [validation](VALIDATION.md) for recorded results and boundaries. Submit synthetic reproductions only; do not attach private dotenv files or real identifiers.

[Demand research](DEMAND.md) links original user requests and mature alternatives (XlsxWriter, RHash, BagIt, dotenv-linter, dotenv-safe). These tools are intentionally small conveniences, not claims of novel algorithms, unmet markets or proven commercial demand.
