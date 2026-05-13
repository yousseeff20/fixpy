# fixpy 🔍

> **Smart Python traceback explainer — understand your errors instantly.**

[![CI](https://github.com/yousseeff20/fixpy/actions/workflows/ci.yml/badge.svg)](https://github.com/yousseeff20/fixpy/actions)
[![PyPI version](https://badge.fury.io/py/fixpy-traceback.svg)](https://pypi.org/project/fixpy-traceback/)
[![Python](https://img.shields.io/pypi/pyversions/fixpy-traceback)](https://pypi.org/project/fixpy-traceback/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

fixpy analyses Python tracebacks and explains them in **plain, beginner-friendly English** (and Arabic!) with:

- 🎨 **Beautiful Rich terminal output** — color-coded panels, syntax-highlighted code examples
- 🔍 **14 exception analyzers** — SyntaxError, NameError, TypeError, AttributeError, ImportError, and more
- 💡 **Smart suggestions** — typo detection, `pip install` hints, NoneType detection
- 🌐 **Arabic mode** — `--lang ar` for Arabic explanations
- 👁 **Watch mode** — re-analyse on every file save
- 📋 **Clipboard support** — paste tracebacks directly
- 🔧 **JSON output** — for CI/CD integration
- 🐍 **Python 3.9–3.13** compatible

---

## Installation

```bash
pip install fixpy-traceback
```

Or for development:

```bash
git clone https://github.com/yousseeff20/fixpy
cd fixpy
pip install -e ".[dev]"
```

---

## Usage

### Analyse a log file
```bash
fixpy error.log
```

### Run a script and analyse its error
```bash
fixpy app.py
```

### Pipe output directly
```bash
python app.py 2>&1 | fixpy
```

### Paste a traceback from clipboard
```bash
fixpy --paste
```

### Watch mode — re-analyse on every save
```bash
fixpy --watch app.py
```

### Arabic output
```bash
fixpy --lang ar error.log
```

### Machine-readable JSON output
```bash
fixpy --json error.log
```

---

## Example Output

```
╔══════════════════════════════════════════════════════════════╗
║   ZeroDivisionError   fixpy — Error Detected                 ║
╚══════════════════════════════════════════════════════════════╝

┌─ 📍 Error Location ──────────────────────────────────────────┐
│  📄 File      app.py                                          │
│  📍 Line      5                                               │
│  ⚙  Function  <module>                                        │
│  💬 Code      result = 10 / 0                                 │
└───────────────────────────────────────────────────────────────┘

┌─ 🔍 What Happened ────────────────────────────────────────────┐
│  Division by zero: used `/` with a denominator of 0.          │
└───────────────────────────────────────────────────────────────┘

┌─ 📖 Why It Happened ──────────────────────────────────────────┐
│  In mathematics, dividing by zero is undefined. Python raises  │
│  ZeroDivisionError whenever the right-hand side of `/` is 0.  │
└───────────────────────────────────────────────────────────────┘

┌─ 🛠  How to Fix It ────────────────────────────────────────────┐
│  Check that the denominator is not zero before dividing,       │
│  or use a try/except block to handle the case gracefully.      │
└───────────────────────────────────────────────────────────────┘

┌─ ✅ Fixed Code Example ────────────────────────────────────────┐
│  def safe_divide(a, b):                                        │
│      if b == 0:                                                │
│          return None                                           │
│      return a / b                                              │
└───────────────────────────────────────────────────────────────┘

  Confidence: ████████████████████░ 97%  (pattern-based — not AI)
  👶 Common Beginner Mistake
```

---

## Supported Exceptions

| Exception | Confidence | Features |
|---|---|---|
| `SyntaxError` | 88–95% | Sub-type detection, indentation hints |
| `IndentationError` | 95% | Tab/space mix detection |
| `NameError` | 88% | Typo suggestions, import hints |
| `TypeError` | 70–90% | NoneType patterns, operand types, arg count |
| `AttributeError` | 85–90% | NoneType detection, per-type suggestions |
| `ImportError` | 88% | `pip install` mapping for 30+ packages |
| `ModuleNotFoundError` | 95% | Smart pip package name lookup |
| `IndexError` | 92% | Zero-indexing explanation |
| `KeyError` | 92% | Safe `.get()` pattern |
| `ZeroDivisionError` | 97% | Guard patterns, try/except example |
| `ValueError` | 72–93% | int/float conversion, unpacking |
| `FileNotFoundError` | 94% | Path tips, pathlib example |
| `RuntimeError` | 60–95% | Dict mutation, bare raise detection |
| `RecursionError` | 96% | Base case explanation, function detection |

---

## CLI Reference

```
Usage: fixpy [OPTIONS] [SOURCE]

  fixpy — Analyse a Python traceback and explain it in plain English.

Arguments:
  [SOURCE]  Path to a .py script or .log/.txt traceback file.

Options:
  -p, --paste         Read traceback from the system clipboard.
  -w, --watch         Watch a .py file — re-analyse on every save.
  -l, --lang TEXT     Output language: 'en' (default) or 'ar'.
  --json              Output analysis as machine-readable JSON.
  -v, --version       Show version and exit.
  --help              Show this message and exit.
```

---

## Building from Source

```bash
# Install build tool
pip install hatch

# Build wheel + sdist
hatch build

# Output is in dist/
ls dist/
```

---

## Publishing to PyPI

```bash
# 1. Update version in pyproject.toml and src/fixpy/__init__.py
# 2. Create and push a version tag
git tag v0.1.0
git push origin v0.1.0

# GitHub Actions will automatically build and publish to PyPI
# via trusted publishing (no API keys needed).

# Or publish manually:
pip install twine
twine upload dist/*
```

---

## Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# With coverage report
pytest --cov=fixpy --cov-report=html

# Lint
ruff check src/
```

---

## Project Structure

```
fixpy/
├── src/fixpy/
│   ├── cli.py                    # Typer CLI entry point
│   ├── models.py                 # Core dataclasses
│   ├── parser/                   # Traceback text parser
│   ├── analyzers/                # 14 exception analyzers + registry
│   │   └── exceptions/
│   ├── formatter/                # Rich terminal renderer
│   ├── i18n/                     # English + Arabic strings
│   └── helpers/                  # Clipboard, file watcher, similarity
├── tests/                        # pytest test suite
├── examples/                     # Sample .log files
└── .github/workflows/ci.yml      # GitHub Actions CI
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT © fixpy Contributors
