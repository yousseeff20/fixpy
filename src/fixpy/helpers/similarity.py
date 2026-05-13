"""
difflib-based name similarity helper.

Used by NameError and AttributeError analyzers to suggest correct names
when a typo is suspected.
"""

from __future__ import annotations

import difflib


def find_similar_names(
    target: str,
    candidates: list[str],
    n: int = 5,
    cutoff: float = 0.6,
) -> list[str]:
    """
    Return up to *n* names from *candidates* that are similar to *target*.

    Uses SequenceMatcher ratio — cutoff 0.6 is a reasonable balance between
    precision (not too loose) and recall (catches common typos).
    """
    return difflib.get_close_matches(target, candidates, n=n, cutoff=cutoff)


# Common Python builtins — searched when the exact scope is unavailable
PYTHON_BUILTINS: list[str] = [
    "print", "len", "range", "type", "int", "str", "float", "bool",
    "list", "dict", "set", "tuple", "input", "open", "enumerate",
    "zip", "map", "filter", "sorted", "reversed", "sum", "min", "max",
    "abs", "round", "isinstance", "issubclass", "hasattr", "getattr",
    "setattr", "delattr", "callable", "repr", "id", "hash", "dir",
    "vars", "help", "any", "all", "next", "iter", "format", "chr",
    "ord", "bin", "oct", "hex", "bytes", "bytearray", "memoryview",
    "object", "super", "classmethod", "staticmethod", "property",
    "Exception", "ValueError", "TypeError", "KeyError", "IndexError",
    "AttributeError", "NameError", "ImportError", "OSError",
    "FileNotFoundError", "RuntimeError", "StopIteration", "None",
    "True", "False", "NotImplemented", "Ellipsis",
]
