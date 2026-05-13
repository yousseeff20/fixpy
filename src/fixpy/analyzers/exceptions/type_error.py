"""TypeError analyzer."""

from __future__ import annotations

import re

from ...models import Analysis, ParsedTraceback
from ..base import BaseAnalyzer

_UNSUPPORTED_OP = re.compile(
    r"unsupported operand type\(s\) for (.+): '(.+)' and '(.+)'"
)
_NOT_CALLABLE = re.compile(r"'(.+)' object is not callable")
_MISSING_ARGS = re.compile(r"(\w+)\(\) (missing|takes) (\d+|no) required positional argument")
_NOT_SUBSCRIPTABLE = re.compile(r"'(.+)' object is not subscriptable")
_NOT_ITERABLE = re.compile(r"'(.+)' object is not iterable")
_NONE_NOT_SUBSCRIPTABLE = re.compile(r"'NoneType' object is not subscriptable")
_NONE_NOT_ITERABLE = re.compile(r"'NoneType' object is not iterable")
_NONE_NOT_CALLABLE = re.compile(r"'NoneType' object is not callable")


class TypeErrorAnalyzer(BaseAnalyzer):
    """Handles TypeError with multiple sub-type patterns."""

    def can_handle(self, parsed: ParsedTraceback) -> bool:
        return parsed.exception_type == "TypeError"

    def analyze(self, parsed: ParsedTraceback) -> Analysis:
        msg = parsed.message

        # ── NoneType patterns (function returned None unexpectedly) ──────────
        if _NONE_NOT_SUBSCRIPTABLE.search(msg):
            return self._none_result_analysis(parsed, "subscript (use [])")
        if _NONE_NOT_ITERABLE.search(msg):
            return self._none_result_analysis(parsed, "iterate over (use in a loop)")
        if _NONE_NOT_CALLABLE.search(msg):
            return self._none_result_analysis(parsed, "call (use ())")

        # ── Unsupported operand ───────────────────────────────────────────────
        m = _UNSUPPORTED_OP.search(msg)
        if m:
            op, t1, t2 = m.group(1), m.group(2), m.group(3)
            return Analysis(
                exception_type="TypeError",
                cause=f"Cannot use `{op}` between `{t1}` and `{t2}`.",
                explanation=(
                    f"Python doesn't know how to apply the `{op}` operator to a "
                    f"`{t1}` and a `{t2}`. The most common cause is accidentally "
                    f"mixing a string with a number."
                ),
                fix=(
                    "Convert one of the values so both sides have the same type. "
                    "For example, use `int()`, `float()`, or `str()` to convert."
                ),
                code_example=(
                    "# ✅ Convert types before operating\n"
                    "age = input('Enter age: ')  # input() returns a string\n"
                    "age = int(age)              # convert to int first\n"
                    "print(age + 5)\n"
                ),
                confidence=0.90,
                is_beginner_mistake=True,
                stack_explanation=self._build_stack_explanation(parsed),
                smart_suggestions=[
                    "Use `type(value)` to inspect a variable's type.",
                    "Remember: `input()` always returns a string.",
                ],
                ar_cause=f"لا يمكن استخدام العملية `{op}` بين `{t1}` و`{t2}`.",
                ar_explanation="بايثون لا يعرف كيف يطبق هذه العملية على هذين النوعين. قد تكون تخلط بين string و number.",
                ar_fix="حوّل أحد القيمتين لتكونا من نفس النوع باستخدام int() أو str().",
            )

        # ── Not callable ──────────────────────────────────────────────────────
        m = _NOT_CALLABLE.search(msg)
        if m:
            obj_type = m.group(1)
            return Analysis(
                exception_type="TypeError",
                cause=f"You tried to call a `{obj_type}` object as if it were a function.",
                explanation=(
                    f"Only functions, methods, and classes are callable. "
                    f"A `{obj_type}` is a value, not a function. "
                    f"Check if you accidentally added `()` after a variable."
                ),
                fix=(
                    "Remove the `()` if you don't intend to call it, or check that "
                    "the variable holds a function, not a value."
                ),
                code_example=(
                    "# ✅ Don't add () to non-functions\n"
                    "numbers = [1, 2, 3]\n"
                    "print(numbers[0])   # ← access by index, not call\n"
                ),
                confidence=0.85,
                is_beginner_mistake=True,
                stack_explanation=self._build_stack_explanation(parsed),
                smart_suggestions=[
                    f"Check if `{obj_type}` was overwritten — e.g., `list = [1,2,3]` shadows the built-in.",
                ],
                ar_cause=f"حاولت استدعاء كائن `{obj_type}` كأنه دالة.",
                ar_explanation="فقط الدوال والكلاسات قابلة للاستدعاء. ربما أضفت () بعد متغير عادي.",
                ar_fix="احذف () إذا لم تكن تريد استدعاءه، أو تحقق أن المتغير يحتوي على دالة.",
            )

        # ── Missing arguments ─────────────────────────────────────────────────
        m = _MISSING_ARGS.search(msg)
        if m:
            func = m.group(1)
            return Analysis(
                exception_type="TypeError",
                cause=f"`{func}()` was called with the wrong number of arguments.",
                explanation=(
                    f"The function `{func}` requires certain positional arguments "
                    f"that you didn't provide (or provided too many)."
                ),
                fix=(
                    f"Check the signature of `{func}` and make sure you pass all "
                    f"required arguments. Use `help({func})` to see what it expects."
                ),
                code_example=(
                    "# ✅ Match arguments to function signature\n"
                    "def greet(name, age):    # needs 2 args\n"
                    "    print(name, age)\n\n"
                    "greet('Alice', 30)       # correct!\n"
                ),
                confidence=0.88,
                is_beginner_mistake=True,
                stack_explanation=self._build_stack_explanation(parsed),
                smart_suggestions=[
                    f"Run `help({func})` in the Python REPL to see its signature.",
                ],
                ar_cause=f"تم استدعاء `{func}()` بعدد خاطئ من الوسائط.",
                ar_explanation=f"الدالة `{func}` تتطلب وسائط معينة لم تُمرَّر.",
                ar_fix=f"تحقق من signature الدالة `{func}` وتأكد من تمرير جميع الوسائط المطلوبة.",
            )

        # ── Generic fallback ──────────────────────────────────────────────────
        return Analysis(
            exception_type="TypeError",
            cause="A value of the wrong type was used in an operation.",
            explanation=(
                "Python is strict about types. You passed a value of a type that "
                "wasn't expected — for example, using a string where a number is "
                "needed, or vice versa."
            ),
            fix="Inspect the types of your variables with `type()` and convert as needed.",
            code_example=(
                "# ✅ Check and convert types\n"
                "value = '42'\n"
                "print(int(value) + 8)  # convert string → int\n"
            ),
            confidence=0.70,
            stack_explanation=self._build_stack_explanation(parsed),
            ar_cause="تم استخدام قيمة من النوع الخاطئ.",
            ar_explanation="بايثون صارم مع الأنواع. تحقق من أنواع المتغيرات باستخدام type().",
            ar_fix="استخدم int() أو str() أو float() لتحويل الأنواع.",
        )

    def _none_result_analysis(self, parsed: ParsedTraceback, op: str) -> Analysis:
        return Analysis(
            exception_type="TypeError",
            cause=f"You tried to {op} a `None` value.",
            explanation=(
                "A variable holds `None` (no value) when:\n"
                "  • A function that doesn't explicitly return anything returns None by default.\n"
                "  • A function like `list.sort()` modifies in place and returns None.\n"
                "  • An API/database call returned no result."
            ),
            fix=(
                "Check the function that produced this value — does it have a `return` "
                "statement? Use `print(value)` before the failing line to inspect it."
            ),
            code_example=(
                "# ✅ sort() returns None — use sorted() instead\n"
                "numbers = [3, 1, 2]\n"
                "# ❌ result = numbers.sort()  # result is None!\n"
                "result = sorted(numbers)       # sorted() returns a new list\n"
                "print(result[0])\n"
            ),
            confidence=0.87,
            is_beginner_mistake=True,
            stack_explanation=self._build_stack_explanation(parsed),
            smart_suggestions=[
                "Remember: `list.sort()`, `list.append()`, `dict.update()` all return None.",
                "Add `assert value is not None` as a guard before using the value.",
            ],
            ar_cause="حاولت استخدام قيمة None.",
            ar_explanation="المتغير يحتوي على None. ربما الدالة لا تُرجع قيمة، أو تُعدّل القائمة في مكانها.",
            ar_fix="تحقق أن الدالة تحتوي على return. استخدم print() لفحص القيمة.",
        )
