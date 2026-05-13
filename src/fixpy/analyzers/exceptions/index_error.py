"""IndexError analyzer."""

from __future__ import annotations

from ...models import Analysis, ParsedTraceback
from ..base import BaseAnalyzer


class IndexErrorAnalyzer(BaseAnalyzer):
    """Handles IndexError."""

    def can_handle(self, parsed: ParsedTraceback) -> bool:
        return parsed.exception_type == "IndexError"

    def analyze(self, parsed: ParsedTraceback) -> Analysis:
        msg = parsed.message.lower()
        is_string = "string" in msg
        obj = "string" if is_string else "list"

        return Analysis(
            exception_type="IndexError",
            cause=f"You accessed an index that is out of the {obj}'s range.",
            explanation=(
                f"Python {obj}s are zero-indexed — the first element is at index 0, "
                f"not 1. If your {obj} has N items, valid indices are 0 to N-1. "
                f"Accessing index N or beyond raises IndexError."
            ),
            fix=(
                f"Check your index value before accessing the {obj}. "
                f"Use `len()` to know the valid range: `0` to `len({obj}) - 1`."
            ),
            code_example=(
                "# ✅ Safe indexed access\n"
                "items = ['a', 'b', 'c']  # indices: 0, 1, 2\n"
                "index = 1\n"
                "if index < len(items):\n"
                "    print(items[index])\n"
                "else:\n"
                "    print('Index out of range!')\n"
            ),
            confidence=0.92,
            is_beginner_mistake=True,
            stack_explanation=self._build_stack_explanation(parsed),
            smart_suggestions=[
                "Remember: Python is zero-indexed. `items[0]` is the FIRST element.",
                "Use negative indices to access from the end: `items[-1]` = last element.",
                "Use a `for item in items:` loop to avoid manual indexing altogether.",
            ],
            ar_cause=f"وصلت إلى فهرس خارج نطاق الـ{obj}.",
            ar_explanation=(
                f"الفهارس تبدأ من 0 في بايثون. إذا كان الـ{obj} يحتوي N عنصراً، "
                f"الفهارس الصالحة هي 0 إلى N-1."
            ),
            ar_fix="تحقق من قيمة الفهرس. استخدم len() لمعرفة الحد الأقصى.",
        )
