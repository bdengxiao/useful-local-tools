---
name: env-preflight
description: Compare a dotenv template with a local dotenv file for missing keys, duplicates, empty values and likely placeholders while keeping values out of the report. Use for static configuration diagnosis, not credential validation or layered framework environment resolution.
---

Run `scripts/env_preflight.py` relative to this skill folder with Python 3.10+. No third-party packages are needed.

```sh
python scripts/env_preflight.py --example /project/.env.example --env /project/.env
python scripts/env_preflight.py --example /project/.env.example --env /project/.env --allow-empty OPTIONAL_KEY
```

Read the JSON report instead of printing the dotenv file. The helper never executes command substitution, expands variables, writes configuration or prints values. Do not paste private values into model context to explain a missing key. Key names and line numbers are sufficient. Key names can still reveal business details; sharing reports externally is a separate action.

Missing required keys, empty required values, heuristic placeholders, duplicates and unsupported syntax fail. Extra keys are informational unless `--strict-extra` is supplied. Allow an empty key only if the user's configuration semantics permit it; typoed exemptions are reported. Placeholders are a small documented heuristic, not credential validity checks. `unexpanded` warns about interpolation-like text; it is not evaluated and does not by itself fail.

Supports UTF-8/BOM, optional `export`, ASCII variable names, single-line values and comments. Multiline quoted values are explicitly unsupported. It does not merge `.env.local`, inherit `process.env`, understand Compose/Next.js precedence or validate remote credentials. Exit codes are 0 passed, 1 findings, 2 unreadable input. Report what needs to change without inventing secret values or overwriting files.
