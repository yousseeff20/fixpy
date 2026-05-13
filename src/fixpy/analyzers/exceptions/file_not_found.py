"""FileNotFoundError analyzer."""

from __future__ import annotations

import re

from ...models import Analysis, ParsedTraceback
from ..base import BaseAnalyzer

_PATH_RE = re.compile(r"\[Errno 2\] No such file or directory: '(.+)'")


class FileNotFoundErrorAnalyzer(BaseAnalyzer):
    """Handles FileNotFoundError."""

    def can_handle(self, parsed: ParsedTraceback) -> bool:
        return parsed.exception_type in ("FileNotFoundError", "IOError", "OSError") and (
            "No such file or directory" in parsed.message
        )

    def analyze(self, parsed: ParsedTraceback) -> Analysis:
        m = _PATH_RE.search(parsed.message)
        path = m.group(1) if m else "<path>"

        return Analysis(
            exception_type="FileNotFoundError",
            cause=f"The file or directory `{path}` does not exist.",
            explanation=(
                f"Python tried to open `{path}` but couldn't find it. Common causes:\n"
                f"  • The path is relative and your script is running from a different directory.\n"
                f"  • The filename has a typo.\n"
                f"  • The file hasn't been created yet.\n"
                f"  • You're using backslashes on Windows inside a string without raw strings."
            ),
            fix=(
                "Check the path carefully. Use `os.path.exists(path)` to verify before opening, "
                "or use `pathlib.Path` for cross-platform paths."
            ),
            code_example=(
                "from pathlib import Path\n\n"
                "# ✅ Check before opening\n"
                f"file_path = Path('{path}')\n"
                "if file_path.exists():\n"
                "    with file_path.open() as f:\n"
                "        content = f.read()\n"
                "else:\n"
                f"    print(f'File not found: {{file_path}}')\n"
            ),
            confidence=0.94,
            is_beginner_mistake=True,
            stack_explanation=self._build_stack_explanation(parsed),
            smart_suggestions=[
                "Run `import os; print(os.getcwd())` to see your current working directory.",
                "Use raw strings for Windows paths: `r'C:\\Users\\name\\file.txt'`",
                "Use `pathlib.Path` — it handles `/` and `\\` automatically.",
            ],
            ar_cause=f"الملف أو المجلد `{path}` غير موجود.",
            ar_explanation=(
                "بايثون حاول فتح الملف لكن لم يجده. قد يكون المسار خاطئاً أو الملف لم يُنشأ بعد."
            ),
            ar_fix="تحقق من المسار. استخدم os.path.exists() للتحقق قبل الفتح.",
        )
