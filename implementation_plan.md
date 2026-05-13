# fixpy — Smart Python Traceback Explainer CLI

A production-ready Python CLI tool that parses Python tracebacks and explains them in beginner-friendly language with colored terminal output, watch mode, clipboard support, and multilingual explanations.

---

## Proposed Project Structure

```
fixpy/
├── src/
│   └── fixpy/
│       ├── __init__.py
│       ├── cli.py                  # Typer CLI entry point
│       ├── parser/
│       │   ├── __init__.py
│       │   └── traceback_parser.py # Raw text → structured ParsedTraceback
│       ├── analyzers/
│       │   ├── __init__.py
│       │   ├── base.py             # Abstract BaseAnalyzer
│       │   ├── registry.py         # Analyzer registry / dispatcher
│       │   └── exceptions/         # One file per exception family
│       │       ├── __init__.py
│       │       ├── syntax_error.py
│       │       ├── name_error.py
│       │       ├── type_error.py
│       │       ├── attribute_error.py
│       │       ├── import_error.py
│       │       ├── index_error.py
│       │       ├── key_error.py
│       │       ├── zero_division.py
│       │       ├── value_error.py
│       │       ├── file_not_found.py
│       │       ├── runtime_error.py
│       │       └── recursion_error.py
│       ├── formatter/
│       │   ├── __init__.py
│       │   └── rich_formatter.py   # All Rich rendering logic
│       ├── i18n/
│       │   ├── __init__.py
│       │   ├── en.py               # English strings
│       │   └── ar.py               # Arabic strings
│       ├── helpers/
│       │   ├── __init__.py
│       │   ├── clipboard.py        # pyperclip wrapper
│       │   ├── file_watcher.py     # watchdog wrapper
│       │   └── similarity.py       # difflib-based name suggestion
│       └── models.py               # Dataclasses: ParsedTraceback, Analysis
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_parser.py
│   ├── test_analyzers.py
│   └── test_formatter.py
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions: test matrix + lint
├── pyproject.toml
├── README.md
└── CONTRIBUTING.md
```

---

## Proposed Changes

### Core Data Models — `models.py`

#### [NEW] models.py
- `StackFrame` dataclass: file, line number, function name, source snippet
- `ParsedTraceback` dataclass: exception type, message, full stack frames, raw text
- `Analysis` dataclass: cause, explanation (EN+AR), fix suggestion, code example, confidence score (0–1), pip install hint, beginner flag, nearby name suggestions

---

### Parser — `parser/traceback_parser.py`

#### [NEW] traceback_parser.py
Regex-based parser that converts raw traceback text into `ParsedTraceback`:
- Detect `Traceback (most recent call last):`
- Extract each `File "...", line N, in <func>` frame
- Extract exception type and message from final line
- Handle chained exceptions (`During handling of...`)
- Handle `SyntaxError` which has a different layout

---

### Analyzers — `analyzers/`

#### [NEW] base.py
Abstract `BaseAnalyzer` with `can_handle(parsed) -> bool` and `analyze(parsed) -> Analysis`.

#### [NEW] registry.py
`AnalyzerRegistry` that iterates registered analyzers and returns the best match. Falls back to a `GenericAnalyzer` with a lower confidence score.

#### [NEW] exceptions/*.py (14 analyzers)
Each analyzer:
- Returns a human-readable cause in plain English
- Detects beginner patterns (e.g., `None` returned from function, off-by-one)
- Suggests variable names via `difflib.get_close_matches`
- Suggests `pip install <pkg>` for `ModuleNotFoundError`
- Gives corrected code examples
- Assigns confidence score

---

### Formatter — `formatter/rich_formatter.py`

#### [NEW] rich_formatter.py
Renders final `Analysis` using Rich:
- Header panel with gradient title
- Stack trace table with highlighted file/line columns
- Color-coded explanation panel (`[bold red]` for cause, `[green]` for fix)
- Syntax-highlighted code example via `rich.syntax.Syntax`
- Confidence score as a progress bar
- Emoji-annotated sections (🔍 Cause, 💡 Fix, ✅ Example, 🚀 Suggestions)
- Arabic right-to-left aware rendering when `--lang ar`

---

### i18n — `i18n/`

#### [NEW] en.py / ar.py
Simple key→string dictionaries. Each analyzer references keys so the same analysis data renders in either language.

---

### Helpers

#### [NEW] clipboard.py
Wraps `pyperclip.paste()` with a graceful error if clipboard is unavailable.

#### [NEW] file_watcher.py
Wraps `watchdog` `Observer` + `FileSystemEventHandler`. On file change, re-runs the full analysis pipeline and clears the terminal.

#### [NEW] similarity.py
Wraps `difflib.get_close_matches` with sensible defaults for suggesting variable/function names from the traceback message.

---

### CLI — `cli.py`

#### [NEW] cli.py
Typer app with:
| Argument/Option | Description |
|---|---|
| `[source]` | Path to `.py` file or `.log` file (optional positional) |
| `--paste / -p` | Read traceback from clipboard |
| `--watch / -w` | Watch mode — reanalyze on file save |
| `--lang` | `en` (default) or `ar` |
| `--json` | Machine-readable JSON output |
| `--version` | Print version and exit |

Input priority: `--paste` → piped stdin → file argument.

---

### Packaging — `pyproject.toml`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "fixpy"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = ["rich>=13", "typer>=0.12", "pyperclip>=1.8", "watchdog>=4"]

[project.scripts]
fixpy = "fixpy.cli:app"
```

---

### CI — `.github/workflows/ci.yml`
Matrix test across Python 3.9–3.13 on ubuntu-latest + windows-latest.  
Steps: checkout → setup-python → pip install .[dev] → ruff lint → pytest.

---

### Tests — `tests/`
- `test_parser.py`: fixture tracebacks for all 14 exception types, assert parsed fields
- `test_analyzers.py`: feed `ParsedTraceback` to each analyzer, assert key fields in `Analysis`
- `test_formatter.py`: smoke test that formatter produces non-empty string without crashing

---

## Open Questions

> [!IMPORTANT]
> **Watch mode behavior**: When `--watch app.py` is used, should fixpy *run* `app.py` and capture its stderr, or should it just re-read a log file? Running the script is more useful but requires subprocess management and PTY considerations on Windows.

> [!NOTE]
> **Arabic rendering**: Most Windows terminals don't support BiDi RTL text. Should Arabic mode fall back to a note saying "install Windows Terminal" or render left-to-right anyway?

> [!NOTE]
> **Confidence scoring**: Scores are heuristic (regex + keyword matching). Should there be a visible disclaimer that this is pattern-based, not AI-powered?

---

## Verification Plan

### Automated Tests
```bash
pip install -e ".[dev]"
pytest tests/ -v --tb=short
ruff check src/
```

### Manual Smoke Tests
```bash
# Pipe mode
python -c "x = 1/0" 2>&1 | fixpy

# File mode
fixpy examples/zero_division.log

# Paste mode
fixpy --paste

# Arabic mode
fixpy --lang ar examples/name_error.log

# Watch mode
fixpy --watch examples/sample_app.py

# JSON output
fixpy --json examples/import_error.log
```
