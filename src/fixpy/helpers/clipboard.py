"""
Clipboard helper — wraps pyperclip with graceful error handling.

pyperclip raises PyperclipException on headless systems or when no
clipboard mechanism is available. We catch that and surface a friendly
message instead of a raw traceback.
"""

from __future__ import annotations


def read_clipboard() -> str | None:
    """
    Read text from the system clipboard.

    Returns None and prints a warning if clipboard access fails.
    """
    try:
        import pyperclip  # type: ignore[import]

        text = pyperclip.paste()
        if not isinstance(text, str) or not text.strip():
            return None
        return text
    except Exception as exc:  # pyperclip.PyperclipException or ImportError
        from rich.console import Console

        Console(stderr=True).print(
            f"[yellow]⚠ Clipboard unavailable:[/yellow] {exc}\n"
            "  Try installing [bold]xclip[/bold] or [bold]xsel[/bold] on Linux.",
        )
        return None
