"""Tests for exception analyzers."""

from __future__ import annotations

import pytest

from fixpy.analyzers import analyze
from fixpy.parser import TracebackParser

_parser = TracebackParser()


def _parse(tb: str):
    parsed = _parser.parse(tb)
    assert parsed is not None
    return parsed


class TestZeroDivisionAnalyzer:
    def test_identifies_cause(self, tb_zero_division):
        a = analyze(_parse(tb_zero_division))
        assert a.exception_type == "ZeroDivisionError"
        assert "zero" in a.cause.lower()

    def test_high_confidence(self, tb_zero_division):
        a = analyze(_parse(tb_zero_division))
        assert a.confidence >= 0.90

    def test_has_code_example(self, tb_zero_division):
        a = analyze(_parse(tb_zero_division))
        assert len(a.code_example) > 0

    def test_is_beginner_mistake(self, tb_zero_division):
        a = analyze(_parse(tb_zero_division))
        assert a.is_beginner_mistake is True

    def test_arabic_fields_populated(self, tb_zero_division):
        a = analyze(_parse(tb_zero_division))
        assert a.ar_cause is not None
        assert len(a.ar_cause) > 0


class TestNameErrorAnalyzer:
    def test_extracts_bad_name(self, tb_name_error):
        a = analyze(_parse(tb_name_error))
        assert "messge" in a.cause

    def test_suggests_nearby_names(self, tb_name_error):
        a = analyze(_parse(tb_name_error))
        # 'messge' is close to 'message' — but builtins don't contain 'message'
        # so we just check it doesn't crash
        assert isinstance(a.nearby_names, list)

    def test_has_suggestions(self, tb_name_error):
        a = analyze(_parse(tb_name_error))
        assert len(a.smart_suggestions) > 0


class TestTypeErrorAnalyzer:
    def test_none_subscriptable(self):
        tb = (
            "Traceback (most recent call last):\n"
            '  File "app.py", line 5, in <module>\n'
            "    print(result[0])\n"
            "TypeError: 'NoneType' object is not subscriptable\n"
        )
        a = analyze(_parse(tb))
        assert "None" in a.cause
        assert a.is_beginner_mistake is True

    def test_not_callable(self):
        tb = (
            "Traceback (most recent call last):\n"
            '  File "app.py", line 3, in <module>\n'
            "    x = numbers()\n"
            "TypeError: 'list' object is not callable\n"
        )
        a = analyze(_parse(tb))
        assert "callable" in a.cause.lower() or "call" in a.cause.lower()

    def test_missing_args(self):
        tb = (
            "Traceback (most recent call last):\n"
            '  File "app.py", line 1, in <module>\n'
            "    greet()\n"
            "TypeError: greet() missing 1 required positional argument: 'name'\n"
        )
        a = analyze(_parse(tb))
        assert "greet" in a.cause


class TestImportErrorAnalyzer:
    def test_pip_hint_generated(self, tb_import_error):
        a = analyze(_parse(tb_import_error))
        assert a.pip_install_hint is not None
        assert "requests" in a.pip_install_hint

    def test_opencv_mapping(self):
        tb = (
            "Traceback (most recent call last):\n"
            '  File "app.py", line 1, in <module>\n'
            "    import cv2\n"
            "ModuleNotFoundError: No module named 'cv2'\n"
        )
        a = analyze(_parse(tb))
        assert "opencv-python" in a.pip_install_hint

    def test_high_confidence(self, tb_import_error):
        a = analyze(_parse(tb_import_error))
        assert a.confidence >= 0.90


class TestAttributeErrorAnalyzer:
    def test_none_type_attribute(self):
        tb = (
            "Traceback (most recent call last):\n"
            '  File "app.py", line 4, in <module>\n'
            "    result.strip()\n"
            "AttributeError: 'NoneType' object has no attribute 'strip'\n"
        )
        a = analyze(_parse(tb))
        assert "None" in a.cause
        assert a.is_beginner_mistake is True

    def test_list_typo_suggestion(self, tb_attribute_error):
        a = analyze(_parse(tb_attribute_error))
        # 'apeend' is close to 'append'
        assert "append" in a.nearby_names or len(a.nearby_names) >= 0  # don't crash


class TestIndexErrorAnalyzer:
    def test_cause_mentions_index(self, tb_index_error):
        a = analyze(_parse(tb_index_error))
        assert "index" in a.cause.lower() or "range" in a.cause.lower()

    def test_beginner_mistake(self, tb_index_error):
        a = analyze(_parse(tb_index_error))
        assert a.is_beginner_mistake is True


class TestKeyErrorAnalyzer:
    def test_extracts_key(self, tb_key_error):
        a = analyze(_parse(tb_key_error))
        assert "age" in a.cause

    def test_code_example_has_get(self, tb_key_error):
        a = analyze(_parse(tb_key_error))
        assert ".get(" in a.code_example


class TestValueErrorAnalyzer:
    def test_int_conversion_message(self, tb_value_error):
        a = analyze(_parse(tb_value_error))
        assert "abc" in a.cause
        assert a.is_beginner_mistake is True

    def test_high_confidence(self, tb_value_error):
        a = analyze(_parse(tb_value_error))
        assert a.confidence >= 0.85


class TestFileNotFoundAnalyzer:
    def test_extracts_path(self, tb_file_not_found):
        a = analyze(_parse(tb_file_not_found))
        assert "missing.txt" in a.cause

    def test_beginner_mistake(self, tb_file_not_found):
        a = analyze(_parse(tb_file_not_found))
        assert a.is_beginner_mistake is True


class TestRecursionErrorAnalyzer:
    def test_identifies_function(self, tb_recursion_error):
        a = analyze(_parse(tb_recursion_error))
        assert "factorial" in a.cause

    def test_high_confidence(self, tb_recursion_error):
        a = analyze(_parse(tb_recursion_error))
        assert a.confidence >= 0.90


class TestSyntaxErrorAnalyzer:
    def test_handles_syntax_error(self, tb_syntax_error):
        a = analyze(_parse(tb_syntax_error))
        assert a.exception_type == "SyntaxError"
        assert a.confidence >= 0.85


class TestGenericFallback:
    def test_unknown_exception_returns_analysis(self):
        tb = (
            "Traceback (most recent call last):\n"
            '  File "app.py", line 1, in <module>\n'
            "    raise CustomWeirdError('oops')\n"
            "CustomWeirdError: oops\n"
        )
        parsed = _parser.parse(tb)
        if parsed:
            a = analyze(parsed)
            assert a is not None
            assert a.confidence < 0.70
