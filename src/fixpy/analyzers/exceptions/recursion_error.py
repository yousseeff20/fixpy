"""RecursionError analyzer."""

from __future__ import annotations

from ...models import Analysis, ParsedTraceback
from ..base import BaseAnalyzer


class RecursionErrorAnalyzer(BaseAnalyzer):
    """Handles RecursionError."""

    def can_handle(self, parsed: ParsedTraceback) -> bool:
        return parsed.exception_type == "RecursionError"

    def analyze(self, parsed: ParsedTraceback) -> Analysis:
        # Detect the recursive function name from the stack frames
        func_names = [f.function_name for f in parsed.frames if f.function_name != "<module>"]
        repeating = None
        if func_names:
            # The most frequently occurring name is likely the recursive one
            repeating = max(set(func_names), key=func_names.count)

        func_str = f"`{repeating}`" if repeating else "your function"

        return Analysis(
            exception_type="RecursionError",
            cause=f"{func_str} keeps calling itself forever (infinite recursion).",
            explanation=(
                f"Python limits the call stack to ~1000 levels to prevent memory exhaustion. "
                f"{func_str} calls itself recursively without ever reaching a base case "
                f"that stops the recursion, causing the stack to overflow."
            ),
            fix=(
                "Every recursive function needs a **base case** — a condition where it "
                "stops calling itself and returns a value directly."
            ),
            code_example=(
                "# ❌ Infinite recursion — no base case\n"
                "def countdown(n):\n"
                "    print(n)\n"
                "    countdown(n - 1)  # always calls itself!\n\n"
                "# ✅ With base case\n"
                "def countdown(n):\n"
                "    if n <= 0:        # base case — stop here\n"
                "        return\n"
                "    print(n)\n"
                "    countdown(n - 1)\n"
            ),
            confidence=0.96,
            is_beginner_mistake=True,
            stack_explanation=self._build_stack_explanation(parsed),
            smart_suggestions=[
                f"Look for the base case in {func_str} — it's missing or never reached.",
                "Consider converting deep recursion to an iterative loop.",
                "You can increase the limit with `sys.setrecursionlimit(N)` — but fix the logic first!",
            ],
            ar_cause=f"{func_str} تستدعي نفسها إلى ما لا نهاية (استدعاء ذاتي لا نهائي).",
            ar_explanation=(
                "بايثون يحدد عمق المكدس بـ ~1000 مستوى. "
                f"{func_str} تستدعي نفسها دون الوصول إلى حالة أساسية توقف التكرار."
            ),
            ar_fix="أضف حالة أساسية (base case) تُوقف الاستدعاء الذاتي عند تحقق شرط معين.",
        )
