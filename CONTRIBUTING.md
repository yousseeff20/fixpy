# Contributing to fixpy

Thank you for considering contributing! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/yourusername/fixpy
cd fixpy
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/ -v
```

## Code Style

We use [ruff](https://github.com/astral-sh/ruff) for linting:

```bash
ruff check src/
```

## Adding a New Exception Analyzer

1. Create `src/fixpy/analyzers/exceptions/your_error.py` extending `BaseAnalyzer`.
2. Implement `can_handle()` and `analyze()`.
3. Export it from `src/fixpy/analyzers/exceptions/__init__.py`.
4. Register it in `src/fixpy/analyzers/registry.py` (before `GenericAnalyzer`).
5. Add fixtures + tests in `tests/test_analyzers.py`.

## Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add StopIteration analyzer
fix: handle empty message in KeyError
docs: update README usage examples
test: add ValueError unpacking test
```

## Pull Request Checklist

- [ ] Tests pass (`pytest`)
- [ ] Linting passes (`ruff check src/`)
- [ ] New code has type hints and docstrings
- [ ] Arabic fields populated in any new `Analysis` objects

## License

By contributing, you agree your contributions will be licensed under the MIT License.
