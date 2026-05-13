"""ValueError analyzer."""

from __future__ import annotations

import re

from ...models import Analysis, ParsedTraceback
from ..base import BaseAnalyzer

_INT_CONV = re.compile(r"invalid literal for int\(\) with base \d+: '(.+)'")
_FLOAT_CONV = re.compile(r"could not convert string to float: '(.+)'")
_TOO_MANY_VALUES = re.compile(r"too many values to unpack")
_NOT_ENOUGH_VALUES = re.compile(r"not enough values to unpack")


class ValueErrorAnalyzer(BaseAnalyzer):
    """Handles ValueError."""

    def can_handle(self, parsed: ParsedTraceback) -> bool:
        return parsed.exception_type == "ValueError"

    def analyze(self, parsed: ParsedTraceback) -> Analysis:
        msg = parsed.message

        m = _INT_CONV.search(msg)
        if m:
            bad_val = m.group(1)
            return Analysis(
                exception_type="ValueError",
                cause=f"Cannot convert `'{bad_val}'` to an integer.",
                explanation=(
                    f"`int()` only works on strings that look like whole numbers "
                    f"(e.g. '42', '-7'). The string `'{bad_val}'` contains characters "
                    f"that aren't digits, so the conversion fails."
                ),
                fix=(
                    "Validate the input before converting, or use a try/except block "
                    "to handle bad values gracefully."
                ),
                code_example=(
                    "# ✅ Safe integer conversion\n"
                    "raw = input('Enter a number: ')\n"
                    "try:\n"
                    "    number = int(raw)\n"
                    "except ValueError:\n"
                    "    print(f'Invalid number: {raw}')\n"
                ),
                confidence=0.93,
                is_beginner_mistake=True,
                stack_explanation=self._build_stack_explanation(parsed),
                smart_suggestions=[
                    "Use `str.isdigit()` to check before calling `int()`.",
                    "For decimals, use `float()` instead of `int()`.",
                    "`input()` always returns a string — always convert explicitly.",
                ],
                ar_cause=f"لا يمكن تحويل `'{bad_val}'` إلى عدد صحيح.",
                ar_explanation=f"`int()` يعمل فقط مع السلاسل التي تبدو كأرقام صحيحة. `'{bad_val}'` يحتوي على محارف غير رقمية.",
                ar_fix="تحقق من المدخل قبل التحويل، أو استخدم try/except.",
            )

        m = _FLOAT_CONV.search(msg)
        if m:
            bad_val = m.group(1)
            return Analysis(
                exception_type="ValueError",
                cause=f"Cannot convert `'{bad_val}'` to a float.",
                explanation=f"The string `'{bad_val}'` cannot be interpreted as a decimal number.",
                fix="Validate input or wrap with try/except before calling `float()`.",
                code_example=(
                    "try:\n"
                    f"    value = float('{bad_val}')\n"
                    "except ValueError:\n"
                    "    print('Not a valid number')\n"
                ),
                confidence=0.92,
                is_beginner_mistake=True,
                stack_explanation=self._build_stack_explanation(parsed),
                ar_cause=f"لا يمكن تحويل `'{bad_val}'` إلى عدد عشري.",
                ar_explanation=f"السلسلة `'{bad_val}'` لا تمثل رقماً عشرياً صالحاً.",
                ar_fix="استخدم try/except قبل استدعاء float().",
            )

        if _TOO_MANY_VALUES.search(msg):
            return Analysis(
                exception_type="ValueError",
                cause="Too many values to unpack — right side has more items than variables.",
                explanation=(
                    "When you write `a, b = some_list`, the list must have exactly "
                    "2 items. If it has more, Python raises this error."
                ),
                fix="Use `a, *rest = some_list` to capture extra values, or slice the list first.",
                code_example=(
                    "# ✅ Use starred unpacking for extras\n"
                    "first, *rest = [1, 2, 3, 4]\n"
                    "print(first)  # 1\n"
                    "print(rest)   # [2, 3, 4]\n"
                ),
                confidence=0.88,
                stack_explanation=self._build_stack_explanation(parsed),
                ar_cause="قيم أكثر مما يمكن فك تعبئته.",
                ar_explanation="الجانب الأيمن يحتوي على عناصر أكثر من المتغيرات على اليسار.",
                ar_fix="استخدم first, *rest = list لالتقاط القيم الزائدة.",
            )

        return Analysis(
            exception_type="ValueError",
            cause="An operation received an argument of the right type but wrong value.",
            explanation=(
                "The value passed to a function is syntactically correct (right type) "
                "but semantically wrong — for example, `int('')` or `math.sqrt(-1)`."
            ),
            fix="Validate your data before passing it to functions that have value constraints.",
            code_example=(
                "# ✅ Validate before use\n"
                "import math\n"
                "value = -1\n"
                "if value >= 0:\n"
                "    print(math.sqrt(value))\n"
                "else:\n"
                "    print('Cannot take sqrt of negative number')\n"
            ),
            confidence=0.72,
            stack_explanation=self._build_stack_explanation(parsed),
            ar_cause="تم تمرير قيمة غير صالحة إلى دالة.",
            ar_explanation="النوع صحيح لكن القيمة خاطئة لهذه العملية.",
            ar_fix="تحقق من صحة البيانات قبل تمريرها للدوال.",
        )
