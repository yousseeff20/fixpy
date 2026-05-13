"""
Shared pytest fixtures for fixpy tests.

Fixture convention:
  - Raw traceback strings are prefixed `tb_`
  - ParsedTraceback objects are prefixed `parsed_`
"""

from __future__ import annotations

import pytest

from fixpy.models import ParsedTraceback, StackFrame
from fixpy.parser import TracebackParser

_parser = TracebackParser()


# ─── Raw traceback fixtures ────────────────────────────────────────────────────

@pytest.fixture
def tb_zero_division() -> str:
    return (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 5, in <module>\n'
        "    result = 10 / 0\n"
        "ZeroDivisionError: division by zero\n"
    )


@pytest.fixture
def tb_name_error() -> str:
    return (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 3, in <module>\n'
        "    print(messge)\n"
        "NameError: name 'messge' is not defined\n"
    )


@pytest.fixture
def tb_type_error_operand() -> str:
    return (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 2, in <module>\n'
        "    result = '5' + 3\n"
        "TypeError: can only concatenate str (not \"int\") to str\n"
    )


@pytest.fixture
def tb_index_error() -> str:
    return (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 4, in <module>\n'
        "    print(items[5])\n"
        "IndexError: list index out of range\n"
    )


@pytest.fixture
def tb_key_error() -> str:
    return (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 6, in main\n'
        "    age = data['age']\n"
        "KeyError: 'age'\n"
    )


@pytest.fixture
def tb_import_error() -> str:
    return (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 1, in <module>\n'
        "    import requests\n"
        "ModuleNotFoundError: No module named 'requests'\n"
    )


@pytest.fixture
def tb_attribute_error() -> str:
    return (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 8, in <module>\n'
        "    result = my_list.apeend(4)\n"
        "AttributeError: 'list' object has no attribute 'apeend'\n"
    )


@pytest.fixture
def tb_recursion_error() -> str:
    return (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 2, in factorial\n'
        "    return factorial(n)\n"
        '  File "app.py", line 2, in factorial\n'
        "    return factorial(n)\n"
        "  [Previous line repeated 996 more times]\n"
        "RecursionError: maximum recursion depth exceeded\n"
    )


@pytest.fixture
def tb_syntax_error() -> str:
    return (
        '  File "app.py", line 3\n'
        "    def greet(name)\n"
        "                  ^\n"
        "SyntaxError: invalid syntax\n"
    )


@pytest.fixture
def tb_file_not_found() -> str:
    return (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 2, in <module>\n'
        "    open('missing.txt')\n"
        "FileNotFoundError: [Errno 2] No such file or directory: 'missing.txt'\n"
    )


@pytest.fixture
def tb_value_error() -> str:
    return (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 3, in <module>\n'
        "    n = int('abc')\n"
        "ValueError: invalid literal for int() with base 10: 'abc'\n"
    )


# ─── ParsedTraceback fixtures ──────────────────────────────────────────────────

@pytest.fixture
def parsed_zero_division(tb_zero_division) -> ParsedTraceback:
    return _parser.parse(tb_zero_division)


@pytest.fixture
def parsed_name_error(tb_name_error) -> ParsedTraceback:
    return _parser.parse(tb_name_error)


@pytest.fixture
def parsed_import_error(tb_import_error) -> ParsedTraceback:
    return _parser.parse(tb_import_error)


@pytest.fixture
def parsed_recursion_error(tb_recursion_error) -> ParsedTraceback:
    return _parser.parse(tb_recursion_error)
