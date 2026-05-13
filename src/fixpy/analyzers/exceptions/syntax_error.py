"""SyntaxError and IndentationError analyzer."""

from __future__ import annotations

import re

from ...models import Analysis, ParsedTraceback
from ..base import BaseAnalyzer

_INVALID_SYNTAX = re.compile(r"invalid syntax", re.IGNORECASE)
_UNEXPECTED_EOF = re.compile(r"unexpected EOF|expected an indented block", re.IGNORECASE)
_MISSING_COLON = re.compile(r"invalid syntax.*maybe.*missing.*colon", re.IGNORECASE)


class SyntaxErrorAnalyzer(BaseAnalyzer):
    """Handles SyntaxError and IndentationError."""

    def can_handle(self, parsed: ParsedTraceback) -> bool:
        return parsed.exception_type in (
            "SyntaxError", "IndentationError", "TabError"
        )

    def analyze(self, parsed: ParsedTraceback) -> Analysis:
        msg = parsed.message.lower()
        frame = self._innermost_frame(parsed)
        loc = f" at line {frame.line_number}" if frame else ""

        # Determine sub-type
        if parsed.exception_type == "IndentationError":
            cause = f"IndentationError{loc}: your indentation (spaces/tabs) is inconsistent."
            explanation = (
                "Python uses indentation to define code blocks. If you mix tabs "
                "and spaces, or your indentation levels are inconsistent, Python "
                "cannot parse your file."
            )
            fix = (
                "Use only spaces (4 spaces per level is standard) or only tabs — "
                "never both. Most editors have a 'Convert Indentation' option."
            )
            code_example = (
                "# ✅ Correct — consistent 4-space indentation\n"
                "def greet(name):\n"
                "    if name:\n"
                "        print('Hello', name)\n"
            )
            confidence = 0.95
            ar_cause = f"خطأ في المسافة البادئة{loc}"
            ar_explanation = (
                "بايثون يستخدم المسافة البادئة لتحديد الكتل البرمجية. "
                "إذا خلطت بين المسافات والـ tabs، سيفشل تحليل الملف."
            )
            ar_fix = "استخدم 4 مسافات فقط لكل مستوى. تجنب الخلط بين spaces وtabs."

        elif "unexpected eof" in msg or "expected an indented block" in msg:
            cause = f"SyntaxError{loc}: Python reached the end of file but expected more code."
            explanation = (
                "You likely have an open block (if, for, def, class, try…) "
                "that has no body, or you forgot to close a bracket/parenthesis."
            )
            fix = (
                "Check for unclosed (, [, { — or an if/def/for block with no "
                "indented body. Add `pass` as a placeholder if needed."
            )
            code_example = (
                "# ✅ Every block needs a body\n"
                "def my_function():\n"
                "    pass  # add your code here\n\n"
                "if True:\n"
                "    pass\n"
            )
            confidence = 0.90
            ar_cause = f"SyntaxError{loc}: توصّل بايثون لنهاية الملف وهو يتوقع المزيد."
            ar_explanation = "يوجد قوس أو كتلة مفتوحة لم تُغلق بعد."
            ar_fix = "تحقق من الأقواس غير المغلقة أو الكتل (if/def/for) الفارغة."

        else:
            cause = f"SyntaxError{loc}: Python could not understand your code."
            explanation = (
                "Python's parser found something it didn't expect. Common causes: "
                "a missing colon (:) after if/for/def/class, mismatched brackets, "
                "a stray character, or a reserved keyword used as a variable name."
            )
            fix = (
                "Look at the line indicated — check for a missing `:`, unmatched "
                "`(` or `)`, or a typo. Python points the caret (^) at the "
                "earliest spot where it got confused."
            )
            code_example = (
                "# ✅ Remember colons after if/for/def/class\n"
                "def greet(name):          # ← colon required\n"
                "    print('Hello', name)\n\n"
                "for i in range(10):       # ← colon required\n"
                "    print(i)\n"
            )
            confidence = 0.88
            ar_cause = f"SyntaxError{loc}: لم يستطع بايثون فهم الكود."
            ar_explanation = (
                "أسباب شائعة: نقص النقطتين (:) بعد if/for/def/class، "
                "أو قوس غير مغلق، أو حرف زائد."
            )
            ar_fix = "تحقق من السطر المشار إليه ابحث عن نقطتين ناقصة أو قوس غير مغلق."

        return Analysis(
            exception_type=parsed.exception_type,
            cause=cause,
            explanation=explanation,
            fix=fix,
            code_example=code_example,
            confidence=confidence,
            is_beginner_mistake=True,
            stack_explanation=self._build_stack_explanation(parsed),
            smart_suggestions=[
                "Use an editor with syntax highlighting — it catches these instantly.",
                "Run `python -m py_compile your_file.py` to check syntax before running.",
            ],
            ar_cause=ar_cause,
            ar_explanation=ar_explanation,
            ar_fix=ar_fix,
        )
