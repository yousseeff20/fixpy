"""
Core data models for fixpy.

Architecture note:
    All inter-module communication uses these dataclasses.
    This ensures analyzers, formatters, and the CLI never share mutable state,
    making the pipeline trivially testable and thread-safe.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StackFrame:
    """Represents a single frame in a Python traceback."""

    file: str
    line_number: int
    function_name: str
    source_snippet: str | None = None


@dataclass
class ParsedTraceback:
    """
    Structured representation of a Python traceback.

    Produced by TracebackParser and consumed by analyzers.
    """

    exception_type: str       # e.g. "NameError", "ZeroDivisionError"
    message: str              # The raw error message after the colon
    frames: list[StackFrame]  # Ordered from outermost to innermost call
    raw_text: str             # Original unparsed text
    is_chained: bool = False
    inner_exception: ParsedTraceback | None = None


@dataclass
class Analysis:
    """
    The result of analyzing a ParsedTraceback.

    Produced by an analyzer and consumed by the formatter.
    Contains both English and Arabic fields for i18n support.
    """

    exception_type: str

    # Core explanation fields (English)
    cause: str           # Short one-liner: what caused the error
    explanation: str     # Detailed beginner-friendly explanation
    fix: str             # Actionable fix instructions
    code_example: str    # Corrected code snippet

    # Confidence in this analysis (0.0–1.0, pattern-based heuristic)
    confidence: float

    # Optional enrichments
    pip_install_hint: str | None = None
    is_beginner_mistake: bool = False
    nearby_names: list[str] = field(default_factory=list)
    stack_explanation: list[str] = field(default_factory=list)
    smart_suggestions: list[str] = field(default_factory=list)

    # Arabic i18n fields (populated by analyzers for --lang ar)
    ar_cause: str | None = None
    ar_explanation: str | None = None
    ar_fix: str | None = None
