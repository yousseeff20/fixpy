"""
Analyzer registry — dispatches ParsedTraceback to the right analyzer.

Architecture note:
    Analyzers are tried in registration order. The first analyzer whose
    can_handle() returns True is used. A GenericAnalyzer always matches
    as the final fallback.

    This open/closed design means new analyzers can be added without
    touching existing code — just register them here.
"""

from __future__ import annotations

from ..models import Analysis, ParsedTraceback
from .base import BaseAnalyzer
from .exceptions import (
    AttributeErrorAnalyzer,
    FileNotFoundErrorAnalyzer,
    ImportErrorAnalyzer,
    IndexErrorAnalyzer,
    KeyErrorAnalyzer,
    NameErrorAnalyzer,
    RecursionErrorAnalyzer,
    RuntimeErrorAnalyzer,
    SyntaxErrorAnalyzer,
    TypeErrorAnalyzer,
    ValueErrorAnalyzer,
    ZeroDivisionAnalyzer,
)


class GenericAnalyzer(BaseAnalyzer):
    """Fallback analyzer for unknown exception types."""

    def can_handle(self, parsed: ParsedTraceback) -> bool:
        return True  # Always matches

    def analyze(self, parsed: ParsedTraceback) -> Analysis:
        return Analysis(
            exception_type=parsed.exception_type,
            cause=f"An unrecognised error occurred: {parsed.exception_type}.",
            explanation=(
                f"{parsed.exception_type}: {parsed.message}\n\n"
                "fixpy doesn't have a specific explanation for this error yet. "
                "Read the traceback carefully — the error message usually explains "
                "what went wrong."
            ),
            fix=(
                "Search for the exact error message online, or check the Python "
                "documentation for this exception type."
            ),
            code_example=(
                "# Wrap suspicious code in try/except:\n"
                "try:\n"
                "    your_code()\n"
                f"except {parsed.exception_type} as e:\n"
                "    print(f'Error: {e}')\n"
            ),
            confidence=0.40,
            stack_explanation=self._build_stack_explanation(parsed),
            ar_cause=f"حدث خطأ غير معروف: {parsed.exception_type}.",
            ar_explanation=f"{parsed.exception_type}: {parsed.message}",
            ar_fix="ابحث عن رسالة الخطأ على الإنترنت أو في توثيق بايثون.",
        )


# Ordered list of analyzers — more specific ones first, generic last
_ANALYZERS: list[BaseAnalyzer] = [
    SyntaxErrorAnalyzer(),
    RecursionErrorAnalyzer(),
    ZeroDivisionAnalyzer(),
    FileNotFoundErrorAnalyzer(),
    ImportErrorAnalyzer(),
    NameErrorAnalyzer(),
    AttributeErrorAnalyzer(),
    TypeErrorAnalyzer(),
    IndexErrorAnalyzer(),
    KeyErrorAnalyzer(),
    ValueErrorAnalyzer(),
    RuntimeErrorAnalyzer(),
    GenericAnalyzer(),  # must be last
]


def analyze(parsed: ParsedTraceback) -> Analysis:
    """
    Dispatch *parsed* to the first matching analyzer and return an Analysis.

    Never raises — GenericAnalyzer guarantees a result.
    """
    for analyzer in _ANALYZERS:
        if analyzer.can_handle(parsed):
            return analyzer.analyze(parsed)

    # Unreachable (GenericAnalyzer always matches) but satisfies type checker
    return GenericAnalyzer().analyze(parsed)
