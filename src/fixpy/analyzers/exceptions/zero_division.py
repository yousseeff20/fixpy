"""ZeroDivisionError analyzer."""

from __future__ import annotations

from ...models import Analysis, ParsedTraceback
from ..base import BaseAnalyzer


class ZeroDivisionAnalyzer(BaseAnalyzer):
    """Handles ZeroDivisionError."""

    def can_handle(self, parsed: ParsedTraceback) -> bool:
        return parsed.exception_type == "ZeroDivisionError"

    def analyze(self, parsed: ParsedTraceback) -> Analysis:
        is_modulo = "modulo" in parsed.message.lower()
        op = "%" if is_modulo else "/"

        return Analysis(
            exception_type="ZeroDivisionError",
            cause=f"Division by zero: used `{op}` with a denominator of 0.",
            explanation=(
                "In mathematics, dividing by zero is undefined. Python raises "
                f"ZeroDivisionError whenever the right-hand side of `{op}` is zero. "
                "This often happens when a variable that should be non-zero ends up "
                "being 0 due to unexpected input or a logic error."
            ),
            fix=(
                "Check that the denominator is not zero before dividing, "
                "or use a try/except block to handle the case gracefully."
            ),
            code_example=(
                "# ✅ Guard against division by zero\n"
                "def safe_divide(a, b):\n"
                "    if b == 0:\n"
                "        return None  # or raise a custom error\n"
                "    return a / b\n\n"
                "# Or use try/except:\n"
                "try:\n"
                "    result = a / b\n"
                "except ZeroDivisionError:\n"
                "    print('Cannot divide by zero!')\n"
            ),
            confidence=0.97,
            is_beginner_mistake=True,
            stack_explanation=self._build_stack_explanation(parsed),
            smart_suggestions=[
                "Trace where the denominator value comes from — it may come from user input.",
                "Consider validating inputs at the top of your function.",
                "Use `math.isfinite(result)` after division for extra safety.",
            ],
            ar_cause=f"قسمة على صفر: استُخدم `{op}` مع مقام = 0.",
            ar_explanation=(
                "القسمة على صفر غير معرّفة رياضياً. "
                "هذا يحدث عندما يكون المقسوم عليه صفراً بسبب مدخلات غير متوقعة."
            ),
            ar_fix="تحقق أن المقام ليس صفراً قبل القسمة. استخدم if b != 0 أو try/except.",
        )
