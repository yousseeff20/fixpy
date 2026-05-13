"""AttributeError analyzer."""

from __future__ import annotations

import re

from ...helpers.similarity import find_similar_names
from ...models import Analysis, ParsedTraceback
from ..base import BaseAnalyzer

_ATTR_RE = re.compile(r"'(.+)' object has no attribute '(.+)'")
_NONE_ATTR = re.compile(r"'NoneType' object has no attribute '(.+)'")

_TYPE_ATTRS: dict[str, list[str]] = {
    "str": ["upper", "lower", "strip", "split", "join", "replace", "startswith",
             "endswith", "find", "format", "encode", "title", "count"],
    "list": ["append", "extend", "insert", "remove", "pop", "sort", "reverse",
              "index", "count", "clear", "copy"],
    "dict": ["keys", "values", "items", "get", "update", "pop", "setdefault", "clear"],
}


class AttributeErrorAnalyzer(BaseAnalyzer):
    """Handles AttributeError."""

    def can_handle(self, parsed: ParsedTraceback) -> bool:
        return parsed.exception_type == "AttributeError"

    def analyze(self, parsed: ParsedTraceback) -> Analysis:
        msg = parsed.message

        m = _NONE_ATTR.search(msg)
        if m:
            attr = m.group(1)
            return Analysis(
                exception_type="AttributeError",
                cause=f"You tried to access `.{attr}` on a `None` value.",
                explanation=(
                    "A variable holds `None` and you tried to call a method on it. "
                    "This usually means a function returned `None` — either it has no "
                    "`return` statement, or a condition prevented it from returning."
                ),
                fix=(
                    f"Trace back where the variable comes from. "
                    f"Add `if value is not None:` as a guard before accessing `.{attr}`."
                ),
                code_example=(
                    "# ✅ Guard against None\n"
                    "result = some_function()\n"
                    "if result is not None:\n"
                    f"    result.{attr}()\n"
                ),
                confidence=0.90,
                is_beginner_mistake=True,
                stack_explanation=self._build_stack_explanation(parsed),
                smart_suggestions=[
                    "Functions without `return` implicitly return `None`.",
                    "Methods like `list.sort()` modify in-place and return `None`.",
                ],
                ar_cause=f"حاولت الوصول إلى `.{attr}` على قيمة None.",
                ar_explanation="المتغير يحتوي على None. ربما الدالة لا تُرجع قيمة.",
                ar_fix=f"أضف if result is not None قبل استخدام .{attr}().",
            )

        m = _ATTR_RE.search(msg)
        obj_type = m.group(1) if m else "object"
        attr = m.group(2) if m else "attribute"

        candidates = _TYPE_ATTRS.get(obj_type, [])
        nearby = find_similar_names(attr, candidates) if candidates else []
        suggestions: list[str] = [
            "Use `dir(your_object)` in the Python REPL to see all available attributes.",
        ]
        if nearby:
            suggestions.insert(0, f"Did you mean: {', '.join(f'`.{n}()`' for n in nearby)}?")

        return Analysis(
            exception_type="AttributeError",
            cause=f"`{obj_type}` objects do not have a `.{attr}` attribute.",
            explanation=(
                f"You tried to access `.{attr}` on a `{obj_type}` object, "
                "but that attribute doesn't exist. Likely a typo or wrong object type."
            ),
            fix=f"Check spelling of `.{attr}`. Run `dir(your_object)` to see what's available.",
            code_example=(
                f"# ✅ Inspect available attributes\n"
                f"print(dir(your_{obj_type}_object))\n"
            ),
            confidence=0.85,
            nearby_names=nearby,
            stack_explanation=self._build_stack_explanation(parsed),
            smart_suggestions=suggestions,
            ar_cause=f"كائنات `{obj_type}` لا تملك خاصية `.{attr}`.",
            ar_explanation=f"حاولت الوصول إلى `.{attr}` على `{obj_type}` لكنه غير موجود.",
            ar_fix=f"تحقق من إملاء `.{attr}`. استخدم dir() لرؤية الخصائص المتاحة.",
        )
