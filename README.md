# 🗂️ SortWise

A fast, configurable CLI tool that organizes cluttered directories by file type, date, or custom rules — so you don't have to.

![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

---

## Why SortWise?

We've all had that one `Downloads` folder with 400+ unsorted files. SortWise fixes that in seconds with a single command — and it's smart enough to handle duplicates, nested folders, and custom rules.

## Features

- **Organize by type** — groups files into `Images/`, `Documents/`, `Videos/`, etc.
- **Organize by date** — sorts into `2025/January/`, `2025/February/`, etc.
- **Custom rules** — define your own category mappings via config
- **Dry run mode** — preview changes before committing
- **Undo support** — generates a rollback script with every operation
- **Duplicate handling** — auto-renames collisions instead of overwriting
- **Logging** — full operation log for auditability

## Quick Start

```bash
# Clone the repo
git clone https://github.com/ssuresh808/sortwise.git
cd sortwise

# Install
pip install -e .

# Organize your Downloads by file type
sortwise ~/Downloads --strategy type

# Preview changes without moving anything
sortwise ~/Downloads --strategy date --dry-run

# Use a custom config
sortwise ~/Projects --config my_rules.json
```

## Usage

```
sortwise <directory> [options]

Options:
  --strategy   type | date | custom    Organization strategy (default: type)
  --dry-run                            Preview changes without moving files
  --config     PATH                    Path to custom rules JSON file
  --recursive                          Include files in subdirectories
  --verbose                            Show detailed operation log
```

## Custom Rules

Create a JSON config to define your own categories:

```json
{
  "categories": {
    "Design Assets": [".psd", ".ai", ".fig", ".sketch"],
    "Spreadsheets": [".xlsx", ".csv", ".tsv"],
    "Source Code": [".py", ".js", ".ts", ".go", ".rs"]
  },
  "fallback": "Other"
}
```

## Example Output

```
$ sortwise ~/Downloads --strategy type --verbose

SortWise v1.0.0 — Organizing 47 files in ~/Downloads

  ✓ report_q3.pdf        → Documents/report_q3.pdf
  ✓ photo_001.jpg        → Images/photo_001.jpg
  ✓ photo_001 (1).jpg    → Images/photo_001_2.jpg
  ✓ setup.exe            → Applications/setup.exe
  ✓ notes.txt            → Documents/notes.txt
  ...

Done! Moved 47 files into 6 categories.
Undo script saved to: ~/Downloads/.sortwise_undo.sh
```

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

## Project Structure

```
sortwise/
├── sortwise/
│   ├── __init__.py
│   ├── cli.py           # CLI entry point & argument parsing
│   ├── organizer.py     # Core organization engine
│   ├── strategies.py    # Strategy pattern implementations
│   ├── config.py        # Config file loading & validation
│   └── utils.py         # File helpers & duplicate resolution
├── tests/
│   ├── test_organizer.py
│   ├── test_strategies.py
│   └── test_utils.py
├── setup.py
├── LICENSE
└── README.md
```

## Design Decisions

| Decision | Rationale |
|---|---|
| Strategy pattern | Makes it trivial to add new org methods without touching core logic |
| Dry-run first | Prevents accidental data loss — core design principle |
| Undo scripts | Bash scripts are portable and don't require SortWise to reverse |
| No external deps | Zero dependencies beyond the Python stdlib for maximum portability |

## License

MIT — do whatever you want with it.
