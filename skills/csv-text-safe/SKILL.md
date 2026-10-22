---
name: csv-text-safe
description: Convert CSV or TSV into an Excel workbook while preserving identifiers, leading zeros, long numbers and formula-like strings as literal text. Use for text-faithful spreadsheet handoff, not numerical analysis.
---

Run the bundled `scripts/csv_text_safe.py` with Python 3.10+ and openpyxl 3.1.5+ (`python -m pip install -r requirements.txt` from this skill folder if needed).

```sh
python scripts/csv_text_safe.py input.csv output.xlsx
python scripts/csv_text_safe.py input.tsv output.xlsx --delimiter tab --encoding gb18030
```

Resolve the script relative to this skill directory, not the user's working directory. Use absolute input/output paths when changing working directory. Choose a new output filename: overwrites are refused. All cells, including headers, numbers, dates and `=...`, are literal text. Do not convert numeric-looking IDs to numbers before running this script. Explain that calculations need an intentional later conversion of selected columns.

UTF-8/BOM and comma are the defaults. Use `--delimiter tab` or an explicit one-character delimiter, `--encoding` for known legacy encodings, and `--no-header` if the first row is data. The script does not guess encodings or delimiters. On decoding failure, identify the source encoding rather than using replacement characters. Uneven records, invalid XML characters and Excel limits fail without publishing an output.

After success, report the output path and record count (including the header). Empty strings become blank Excel cells. This cannot restore digits already lost upstream. Script verification is not evidence of a desktop Excel/WPS test. Never upload source data as part of this conversion.
