"""KeyError analyzer."""

from __future__ import annotations

import re

from ...models import Analysis, ParsedTraceback
from ..base import BaseAnalyzer

_KEY_RE = re.compile(r"KeyError: (.+)$", re.MULTILINE)


class KeyErrorAnalyzer(BaseAnalyzer):
    """Handles KeyError."""

    def can_handle(self, parsed: ParsedTraceback) -> bool:
        return parsed.exception_type == "KeyError"

    def analyze(self, parsed: ParsedTraceback) -> Analysis:
        key = parsed.message.strip().strip("'\"") or "<key>"

        return Analysis(
            exception_type="KeyError",
            cause=f"The key `{key}` does not exist in the dictionary.",
            explanation=(
                f"You tried to access `dict['{key}']`, but `'{key}'` is not "
                f"a key in that dictionary. Dictionary keys are case-sensitive "
                f"and must exist before they can be accessed with `[]`."
            ),
            fix=(
                "Use `dict.get(key)` to return `None` instead of raising an error, "
                "or check with `if key in dict:` before accessing."
            ),
            code_example=(
                f"# ✅ Safe dictionary access\n"
                f"data = {{'name': 'Alice', 'age': 30}}\n\n"
                f"# Option 1 — use .get() with a default\n"
                f"value = data.get('{key}', 'not found')\n\n"
                f"# Option 2 — check first\n"
                f"if '{key}' in data:\n"
                f"    print(data['{key}'])\n"
            ),
            confidence=0.92,
            is_beginner_mistake=True,
            stack_explanation=self._build_stack_explanation(parsed),
            smart_suggestions=[
                "Use `dict.get(key, default)` for safe access.",
                "Print `dict.keys()` to see all available keys.",
                "Keys are case-sensitive: `'Name'` ≠ `'name'`.",
            ],
            ar_cause=f"المفتاح `{key}` غير موجود في القاموس.",
            ar_explanation=f"حاولت الوصول إلى `dict['{key}']` لكن هذا المفتاح غير موجود.",
            ar_fix="استخدم dict.get(key) للوصول الآمن، أو تحقق بـ if key in dict.",
        )
