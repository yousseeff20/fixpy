"""Tests for TracebackParser."""

from __future__ import annotations

import pytest

from fixpy.parser import TracebackParser

_parser = TracebackParser()


class TestParserBasics:
    def test_returns_none_on_empty_string(self):
        assert _parser.parse("") is None

    def test_returns_none_on_plain_text(self):
        assert _parser.parse("Hello, world!") is None

    def test_parses_exception_type(self, tb_zero_division):
        parsed = _parser.parse(tb_zero_division)
        assert parsed is not None
        assert parsed.exception_type == "ZeroDivisionError"

    def test_parses_message(self, tb_zero_division):
        parsed = _parser.parse(tb_zero_division)
        assert "division by zero" in parsed.message

    def test_parses_frames(self, tb_zero_division):
        parsed = _parser.parse(tb_zero_division)
        assert len(parsed.frames) == 1
        frame = parsed.frames[0]
        assert frame.file == "app.py"
        assert frame.line_number == 5

    def test_raw_text_preserved(self, tb_zero_division):
        parsed = _parser.parse(tb_zero_division)
        assert parsed.raw_text == tb_zero_division.strip()


class TestParserExceptionTypes:
    def test_name_error(self, tb_name_error):
        parsed = _parser.parse(tb_name_error)
        assert parsed.exception_type == "NameError"
        assert "messge" in parsed.message

    def test_index_error(self, tb_index_error):
        parsed = _parser.parse(tb_index_error)
        assert parsed.exception_type == "IndexError"

    def test_key_error(self, tb_key_error):
        parsed = _parser.parse(tb_key_error)
        assert parsed.exception_type == "KeyError"

    def test_module_not_found_error(self, tb_import_error):
        parsed = _parser.parse(tb_import_error)
        assert parsed.exception_type == "ModuleNotFoundError"

    def test_attribute_error(self, tb_attribute_error):
        parsed = _parser.parse(tb_attribute_error)
        assert parsed.exception_type == "AttributeError"

    def test_file_not_found(self, tb_file_not_found):
        parsed = _parser.parse(tb_file_not_found)
        assert parsed.exception_type == "FileNotFoundError"

    def test_value_error(self, tb_value_error):
        parsed = _parser.parse(tb_value_error)
        assert parsed.exception_type == "ValueError"

    def test_syntax_error(self, tb_syntax_error):
        parsed = _parser.parse(tb_syntax_error)
        assert parsed.exception_type == "SyntaxError"


class TestParserFrames:
    def test_multi_frame(self):
        tb = (
            "Traceback (most recent call last):\n"
            '  File "main.py", line 10, in <module>\n'
            "    result = calculate(5, 0)\n"
            '  File "utils.py", line 4, in calculate\n'
            "    return a / b\n"
            "ZeroDivisionError: division by zero\n"
        )
        parsed = _parser.parse(tb)
        assert len(parsed.frames) == 2
        assert parsed.frames[0].file == "main.py"
        assert parsed.frames[1].file == "utils.py"
        assert parsed.frames[1].function_name == "calculate"

    def test_source_snippet_extracted(self):
        tb = (
            "Traceback (most recent call last):\n"
            '  File "app.py", line 3, in compute\n'
            "    x = 1 / 0\n"
            "ZeroDivisionError: division by zero\n"
        )
        parsed = _parser.parse(tb)
        assert parsed.frames[0].source_snippet == "x = 1 / 0"

    def test_recursion_error_many_frames(self, tb_recursion_error):
        parsed = _parser.parse(tb_recursion_error)
        assert parsed.exception_type == "RecursionError"
        assert len(parsed.frames) >= 1


class TestChainedExceptions:
    def test_chained_is_detected(self):
        tb = (
            "Traceback (most recent call last):\n"
            '  File "a.py", line 1, in <module>\n'
            "    int('x')\n"
            "ValueError: invalid literal for int() with base 10: 'x'\n\n"
            "During handling of the above exception, another exception occurred:\n\n"
            "Traceback (most recent call last):\n"
            '  File "a.py", line 4, in <module>\n'
            "    raise RuntimeError('wrapped')\n"
            "RuntimeError: wrapped\n"
        )
        parsed = _parser.parse(tb)
        assert parsed.is_chained is True
        assert parsed.exception_type == "RuntimeError"
        assert parsed.inner_exception is not None
        assert parsed.inner_exception.exception_type == "ValueError"
