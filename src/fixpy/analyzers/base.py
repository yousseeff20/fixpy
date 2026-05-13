"""
Abstract base analyzer.

Every exception-specific analyzer extends BaseAnalyzer and implements
two methods: can_handle() to declare what it handles and analyze() to
produce an Analysis.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import Analysis, ParsedTraceback


class BaseAnalyzer(ABC):
    """
    Abstract base for all exception analyzers.

    Design note:
        Analyzers are stateless — they receive a ParsedTraceback and return
        a new Analysis object. This makes them easily unit-testable and
        composable through the registry.
    """

    @abstractmethod
    def can_handle(self, parsed: ParsedTraceback) -> bool:
        """Return True if this analyzer can handle the given traceback."""
        ...

    @abstractmethod
    def analyze(self, parsed: ParsedTraceback) -> Analysis:
        """Produce a fully-populated Analysis from the parsed traceback."""
        ...

    # ─── Shared utilities available to all subclasses ─────────────────────────

    @staticmethod
    def _innermost_frame(parsed: ParsedTraceback):
        """Return the last (innermost) stack frame, or None."""
        return parsed.frames[-1] if parsed.frames else None

    @staticmethod
    def _build_stack_explanation(parsed: ParsedTraceback) -> list[str]:
        """Generate a human-readable step-by-step stack walkthrough."""
        steps: list[str] = []
        for i, frame in enumerate(parsed.frames, 1):
            snippet = f" → `{frame.source_snippet}`" if frame.source_snippet else ""
            steps.append(
                f"Step {i}: [{frame.file}:{frame.line_number}] "
                f"in `{frame.function_name}`{snippet}"
            )
        return steps
