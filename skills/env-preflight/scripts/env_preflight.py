"""Compare dotenv keys without executing expressions or printing values."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

KEY = re.compile(r"(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")
PLACEHOLDER = re.compile(r"(?i)^(?:change[_-]?me|replace[_-]?me|your[_-].+|<[^<>]+>|TODO|CHANGEME)$")


def parse(path):
    # Deliberately a strict, single-line subset, not a shell/dotenv interpreter.
    if Path(path).stat().st_size > 4 * 1024 * 1024:
        raise ValueError("File exceeds size limit.")
    values, duplicates, errors = {}, [], []
    with Path(path).open(encoding="utf-8-sig") as stream:
        for number, raw in enumerate(stream, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            match = KEY.fullmatch(line)
            if not match:
                errors.append({"line": number, "reason": "expected KEY=value on one line"})
                continue
            key, value = match.groups()
            if value.startswith(("'", '"')):
                quote = value[0]
                end, escaped = None, False
                for index in range(1, len(value)):
                    char = value[index]
                    if char == quote and not escaped:
                        end = index
                        break
                    escaped = char == "\\" and not escaped if quote == '"' else False
                if end is None or (value[end + 1:].strip() and not value[end + 1:].strip().startswith("#")):
                    errors.append({"line": number, "reason": "invalid or multiline quoted value"})
                    continue
                value = value[1:end]
            else:
                value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
                if value.startswith("#"):
                    value = ""
            if key in values:
                duplicates.append({"key": key, "line": number})
            values[key] = value
    return values, duplicates, errors


def check(example, actual, *, allow_empty=(), strict_extra=False):
    template, template_duplicates, template_errors = parse(example)
    values, duplicates, errors = parse(actual)
    allowed = set(allow_empty)
    unknown_allowed = sorted(allowed - set(template))
    missing = sorted(set(template) - set(values))
    extra = sorted(set(values) - set(template))
    empty = sorted(key for key in template.keys() & values.keys() if not values[key] and key not in allowed)
    placeholders = sorted(key for key in template.keys() & values.keys() if PLACEHOLDER.fullmatch(values[key]))
    unexpanded = sorted(key for key in template.keys() & values.keys() if re.search(r"\$\{|\$\(", values[key]))
    # No value, even on malformed input, is included in the result.
    return {"ok": not (missing or empty or placeholders or duplicates or errors or template_duplicates or
                       template_errors or unknown_allowed or (strict_extra and extra)),
            "missing": missing, "empty": empty, "placeholders": placeholders, "extra": extra,
            "duplicates": duplicates, "syntax_errors": errors,
            "template_duplicates": template_duplicates, "template_errors": template_errors,
            "unknown_allow_empty": unknown_allowed, "unexpanded": unexpanded}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--example", type=Path, default=Path(".env.example"))
    parser.add_argument("--env", type=Path, default=Path(".env"))
    parser.add_argument("--allow-empty", action="append", default=[], metavar="KEY")
    parser.add_argument("--strict-extra", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = check(args.example, args.env, allow_empty=args.allow_empty, strict_extra=args.strict_extra)
    except (OSError, UnicodeError, ValueError):
        # Exception text can contain raw bytes or secrets; never echo it.
        print(json.dumps({"ok": False, "error": "Cannot read inputs. Check paths, UTF-8 encoding and 4 MiB limit."}))
        return 2
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
