"""RuntimeError analyzer."""

from __future__ import annotations

import re

from ...models import Analysis, ParsedTraceback
from ..base import BaseAnalyzer

_DICT_CHANGED = re.compile(r"dictionary changed size during iteration")
_GENERATOR_CLOSED = re.compile(r"generator already executing")
_NO_ACTIVE_EXCEPTION = re.compile(r"No active exception to re-raise")


class RuntimeErrorAnalyzer(BaseAnalyzer):
    """Handles RuntimeError."""

    def can_handle(self, parsed: ParsedTraceback) -> bool:
        return parsed.exception_type == "RuntimeError"

    def analyze(self, parsed: ParsedTraceback) -> Analysis:
        msg = parsed.message

        if _DICT_CHANGED.search(msg):
            return Analysis(
                exception_type="RuntimeError",
                cause="You modified a dictionary while iterating over it.",
                explanation=(
                    "Changing a dictionary's size (adding/removing keys) while looping "
                    "over it is not allowed — Python detects this and raises RuntimeError."
                ),
                fix="Iterate over a copy of the dictionary's keys, or collect changes and apply them after the loop.",
                code_example=(
                    "# ✅ Iterate over a copy\n"
                    "data = {'a': 1, 'b': 2, 'c': 3}\n"
                    "for key in list(data.keys()):  # list() makes a copy\n"
                    "    if data[key] < 2:\n"
                    "        del data[key]\n"
                ),
                confidence=0.95,
                stack_explanation=self._build_stack_explanation(parsed),
                smart_suggestions=[
                    "Use `list(dict.keys())` to safely iterate and modify.",
                    "Collect keys to delete, then delete after the loop.",
                ],
                ar_cause="عدّلت القاموس أثناء المرور عليه.",
                ar_explanation="لا يمكن تغيير حجم القاموس أثناء التكرار عليه.",
                ar_fix="استخدم list(dict.keys()) للتكرار على نسخة من المفاتيح.",
            )

        if _NO_ACTIVE_EXCEPTION.search(msg):
            return Analysis(
                exception_type="RuntimeError",
                cause="Used `raise` outside an exception handler.",
                explanation=(
                    "A bare `raise` statement re-raises the current exception, "
                    "but there is no active exception at that point."
                ),
                fix="Only use bare `raise` inside an `except` block, or raise a specific exception.",
                code_example=(
                    "# ✅ Re-raise inside except\n"
                    "try:\n"
                    "    risky_operation()\n"
                    "except ValueError:\n"
                    "    print('Logging error...')\n"
                    "    raise  # re-raises the ValueError\n"
                ),
                confidence=0.90,
                stack_explanation=self._build_stack_explanation(parsed),
                ar_cause="استُخدم `raise` خارج معالج استثناء.",
                ar_explanation="الـ raise المجرد يُعيد رفع الاستثناء الحالي، لكن لا يوجد استثناء نشط.",
                ar_fix="استخدم raise فقط داخل كتلة except.",
            )

        return Analysis(
            exception_type="RuntimeError",
            cause="A runtime error occurred that doesn't fit a more specific category.",
            explanation=(
                "RuntimeError is a general-purpose error raised when something goes "
                "wrong at runtime that isn't covered by a more specific exception type."
            ),
            fix="Read the full error message carefully — it usually explains what went wrong.",
            code_example=(
                "# Wrap suspicious code in try/except for graceful handling:\n"
                "try:\n"
                "    your_code_here()\n"
                "except RuntimeError as e:\n"
                "    print(f'Runtime error: {e}')\n"
            ),
            confidence=0.60,
            stack_explanation=self._build_stack_explanation(parsed),
            ar_cause="حدث خطأ في وقت التشغيل.",
            ar_explanation="RuntimeError هو خطأ عام يحدث في وقت التشغيل.",
            ar_fix="اقرأ رسالة الخطأ بعناية — عادة تشرح ما حدث.",
        )
