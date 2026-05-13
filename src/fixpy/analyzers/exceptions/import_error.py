"""ImportError and ModuleNotFoundError analyzer."""

from __future__ import annotations

import re

from ...models import Analysis, ParsedTraceback
from ..base import BaseAnalyzer

_MODULE_RE = re.compile(r"No module named '(.+?)'")
_CANNOT_IMPORT = re.compile(r"cannot import name '(.+?)' from '(.+?)'")

# Common package name mappings (import name → pip name)
_PIP_MAP: dict[str, str] = {
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "sklearn": "scikit-learn",
    "bs4": "beautifulsoup4",
    "yaml": "PyYAML",
    "dotenv": "python-dotenv",
    "usb": "pyusb",
    "serial": "pyserial",
    "wx": "wxPython",
    "gi": "PyGObject",
    "gtk": "PyGObject",
    "apt": "python-apt",
    "magic": "python-magic",
    "jwt": "PyJWT",
    "google.cloud": "google-cloud",
    "tensorflow": "tensorflow",
    "torch": "torch",
    "numpy": "numpy",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "requests": "requests",
    "flask": "Flask",
    "django": "Django",
    "fastapi": "fastapi",
    "sqlalchemy": "SQLAlchemy",
    "pydantic": "pydantic",
    "aiohttp": "aiohttp",
    "pytest": "pytest",
    "rich": "rich",
    "typer": "typer",
    "click": "click",
}


def _pip_name(module: str) -> str:
    """Return the pip install name for a module, defaulting to the module name."""
    top_level = module.split(".")[0]
    return _PIP_MAP.get(top_level, top_level)


class ImportErrorAnalyzer(BaseAnalyzer):
    """Handles ImportError and ModuleNotFoundError."""

    def can_handle(self, parsed: ParsedTraceback) -> bool:
        return parsed.exception_type in ("ImportError", "ModuleNotFoundError")

    def analyze(self, parsed: ParsedTraceback) -> Analysis:
        msg = parsed.message

        # ── ModuleNotFoundError ───────────────────────────────────────────────
        m = _MODULE_RE.search(msg)
        if m:
            module = m.group(1)
            pip_pkg = _pip_name(module)
            pip_hint = f"pip install {pip_pkg}"

            return Analysis(
                exception_type=parsed.exception_type,
                cause=f"Python cannot find the module `{module}`.",
                explanation=(
                    f"The module `{module}` is not installed in your current Python "
                    f"environment, or it doesn't exist. This happens when you import "
                    f"a third-party library that hasn't been installed yet."
                ),
                fix=(
                    f"Install the missing package with pip:\n\n"
                    f"    pip install {pip_pkg}\n\n"
                    f"If you're using a virtual environment, make sure it's activated."
                ),
                code_example=(
                    f"# Terminal (run this before your script):\n"
                    f"# pip install {pip_pkg}\n\n"
                    f"# Then in your Python file:\n"
                    f"import {module.split('.')[0]}\n"
                ),
                confidence=0.95,
                pip_install_hint=pip_hint,
                is_beginner_mistake=True,
                stack_explanation=self._build_stack_explanation(parsed),
                smart_suggestions=[
                    f"Run: pip install {pip_pkg}",
                    "If using a venv, activate it first: `source venv/bin/activate` (Linux/macOS) or `venv\\Scripts\\activate` (Windows).",
                    "Check if you have multiple Python versions — use `pip3` if needed.",
                ],
                ar_cause=f"بايثون لا يجد الوحدة `{module}`.",
                ar_explanation=f"الوحدة `{module}` غير مثبتة في بيئتك الحالية.",
                ar_fix=f"ثبّت الحزمة: pip install {pip_pkg}",
            )

        # ── Cannot import name ────────────────────────────────────────────────
        m = _CANNOT_IMPORT.search(msg)
        if m:
            name, from_module = m.group(1), m.group(2)
            return Analysis(
                exception_type="ImportError",
                cause=f"`{name}` does not exist in `{from_module}`.",
                explanation=(
                    f"You tried to import `{name}` from `{from_module}`, but that "
                    f"name doesn't exist there. It may have been renamed, moved, "
                    f"or removed in the version you have installed."
                ),
                fix=(
                    f"Check the documentation for `{from_module}` to find the correct "
                    f"name or location of `{name}`."
                ),
                code_example=(
                    f"# Check what's available in the module:\n"
                    f"import {from_module.split('.')[0]}\n"
                    f"print(dir({from_module.split('.')[0]}))\n"
                ),
                confidence=0.88,
                stack_explanation=self._build_stack_explanation(parsed),
                smart_suggestions=[
                    f"Run: python -c \"import {from_module.split('.')[0]}; print(dir({from_module.split('.')[0]}))\"",
                    "The library may have a different API in your installed version.",
                    f"Try: pip install --upgrade {from_module.split('.')[0]}",
                ],
                ar_cause=f"`{name}` غير موجود في `{from_module}`.",
                ar_explanation="ربما تغيّر الاسم أو نُقل في الإصدار الذي لديك.",
                ar_fix=f"تحقق من توثيق `{from_module}` لمعرفة الاسم أو الموقع الصحيح.",
            )

        # ── Generic fallback ──────────────────────────────────────────────────
        return Analysis(
            exception_type="ImportError",
            cause="A module or name could not be imported.",
            explanation="Python failed to import something. The package may not be installed or the name may be wrong.",
            fix="Check that the package is installed (`pip list`) and the import name is correct.",
            code_example="# pip list | grep <package_name>\n",
            confidence=0.65,
            stack_explanation=self._build_stack_explanation(parsed),
            ar_cause="لم يتمكن بايثون من استيراد وحدة أو اسم.",
            ar_explanation="قد تكون الحزمة غير مثبتة أو الاسم خاطئ.",
            ar_fix="تحقق من تثبيت الحزمة باستخدام pip list.",
        )
