"""NameError analyzer."""

from __future__ import annotations

import re

from ...helpers.similarity import PYTHON_BUILTINS, find_similar_names
from ...models import Analysis, ParsedTraceback
from ..base import BaseAnalyzer

_NAME_RE = re.compile(r"name '(.+?)' is not defined")
_FREE_VAR_RE = re.compile(r"free variable '(.+?)' referenced before assignment")


class NameErrorAnalyzer(BaseAnalyzer):
    """Handles NameError."""

    def can_handle(self, parsed: ParsedTraceback) -> bool:
        return parsed.exception_type == "NameError"

    def analyze(self, parsed: ParsedTraceback) -> Analysis:
        msg = parsed.message
        m = _NAME_RE.search(msg) or _FREE_VAR_RE.search(msg)
        bad_name = m.group(1) if m else "<name>"

        # Collect candidate names from builtins + frame function names
        candidates = list(PYTHON_BUILTINS)
        for frame in parsed.frames:
            candidates.append(frame.function_name)

        nearby = find_similar_names(bad_name, candidates)

        # Detect probable NoneType / unassigned variable pattern
        is_beginner = True
        suggestions: list[str] = [
            f"Make sure you defined `{bad_name}` before using it.",
            "Check for typos — Python is case-sensitive (`myVar` ≠ `myvar`).",
        ]
        if nearby:
            suggestions.insert(0, f"Did you mean: {', '.join(f'`{n}`' for n in nearby)}?")
        if bad_name[0].isupper():
            suggestions.append(
                f"`{bad_name}` starts with a capital letter — did you forget to import it?"
            )

        return Analysis(
            exception_type="NameError",
            cause=f"The name `{bad_name}` does not exist in the current scope.",
            explanation=(
                f"Python couldn't find a variable, function, or class called "
                f"`{bad_name}`. This usually means you either:\n"
                f"  • Misspelled the name (Python is case-sensitive)\n"
                f"  • Used it before assigning a value to it\n"
                f"  • Forgot to import the module that defines it"
            ),
            fix=(
                f"Define `{bad_name}` before you use it, check for typos, "
                f"or add the missing import statement."
            ),
            code_example=(
                f"# ✅ Define the variable before using it\n"
                f"{bad_name} = 'your value here'\n"
                f"print({bad_name})\n"
            ),
            confidence=0.88,
            is_beginner_mistake=is_beginner,
            nearby_names=nearby,
            stack_explanation=self._build_stack_explanation(parsed),
            smart_suggestions=suggestions,
            ar_cause=f"الاسم `{bad_name}` غير موجود في النطاق الحالي.",
            ar_explanation=(
                f"بايثون لم يجد متغيراً أو دالة أو كلاساً باسم `{bad_name}`. "
                "قد تكون نسيت تعريفه، أو أخطأت في كتابته، أو نسيت استيراده."
            ),
            ar_fix=(
                f"عرّف `{bad_name}` قبل استخدامه، أو تحقق من الإملاء، "
                "أو أضف جملة الاستيراد الناقصة."
            ),
        )
