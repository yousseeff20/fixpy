"""Tests for the Rich formatter — smoke tests ensuring no crashes."""

from __future__ import annotations

import pytest
from rich.console import Console

from fixpy.analyzers import analyze
from fixpy.formatter import render
from fixpy.parser import TracebackParser

_parser = TracebackParser()


def _make_console() -> Console:
    """Return an in-memory Console for output capture."""
    from io import StringIO
    return Console(file=StringIO(), highlight=False, width=120)


class TestFormatterSmoke:
    """Smoke tests: render must not raise and must produce non-empty output."""

    def _render_to_string(self, raw_tb: str, lang: str = "en") -> str:
        from io import StringIO
        buf = StringIO()
        console = Console(file=buf, highlight=False, width=120)
        parsed = _parser.parse(raw_tb)
        assert parsed is not None
        analysis = analyze(parsed)
        render(parsed, analysis, lang=lang, console=console)
        return buf.getvalue()

    def test_zero_division_renders(self, tb_zero_division):
        output = self._render_to_string(tb_zero_division)
        assert len(output) > 100

    def test_name_error_renders(self, tb_name_error):
        output = self._render_to_string(tb_name_error)
        assert "NameError" in output

    def test_import_error_renders(self, tb_import_error):
        output = self._render_to_string(tb_import_error)
        assert "ModuleNotFoundError" in output or "pip" in output.lower()

    def test_arabic_renders(self, tb_zero_division):
        output = self._render_to_string(tb_zero_division, lang="ar")
        assert len(output) > 50  # Arabic strings present

    def test_syntax_error_renders(self, tb_syntax_error):
        output = self._render_to_string(tb_syntax_error)
        assert len(output) > 50

    def test_file_not_found_renders(self, tb_file_not_found):
        output = self._render_to_string(tb_file_not_found)
        assert "missing.txt" in output

    def test_recursion_error_renders(self, tb_recursion_error):
        output = self._render_to_string(tb_recursion_error)
        assert "RecursionError" in output or "recursion" in output.lower()

    def test_all_exception_types_render_without_crash(
        self,
        tb_zero_division,
        tb_name_error,
        tb_type_error_operand,
        tb_index_error,
        tb_key_error,
        tb_import_error,
        tb_attribute_error,
        tb_recursion_error,
        tb_syntax_error,
        tb_file_not_found,
        tb_value_error,
    ):
        for tb in [
            tb_zero_division, tb_name_error, tb_type_error_operand,
            tb_index_error, tb_key_error, tb_import_error,
            tb_attribute_error, tb_recursion_error, tb_syntax_error,
            tb_file_not_found, tb_value_error,
        ]:
            output = self._render_to_string(tb)
            assert len(output) > 50, f"Empty output for traceback: {tb[:60]}"
