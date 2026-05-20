"""
fixpy CLI entry point.

Uses Typer for argument parsing and wires together the full pipeline:
  Input source → TracebackParser → Analyzer → Rich Formatter

Input priority:
  1. --paste   (clipboard)
  2. piped stdin
  3. file argument (.log/.txt → read directly; .py → run and capture stderr)
  4. --watch   (watch mode: run file on each save)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

# ── Force UTF-8 output on all platforms (fixes Windows cp1252 issues) ─────────
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import typer
from rich.console import Console

from . import __version__
from .analyzers import analyze
from .formatter import render
from .helpers.clipboard import read_clipboard
from .helpers.file_watcher import watch_file
from .i18n import get_strings
from .parser import TracebackParser

app = typer.Typer(
    name="fixpy",
    help="🔍 Smart Python traceback explainer — understand your errors instantly.",
    add_completion=False,
    rich_markup_mode="rich",
)

_parser = TracebackParser()
_console = Console(highlight=False)
_err_console = Console(stderr=True, highlight=False)


# ─── Version callback ─────────────────────────────────────────────────────────

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"fixpy {__version__}")
        raise typer.Exit()


# ─── Core pipeline ────────────────────────────────────────────────────────────

def _run_pipeline(text: str, lang: str, as_json: bool) -> bool:
    """
    Parse → analyse → render one chunk of traceback text.

    Returns True if a traceback was found and rendered, False otherwise.
    """
    parsed = _parser.parse(text)
    if parsed is None:
        return False

    analysis = analyze(parsed)

    if as_json:
        frame = parsed.frames[-1] if parsed.frames else None
        data = {
            "exception_type": analysis.exception_type,
            "cause": analysis.cause,
            "explanation": analysis.explanation,
            "fix": analysis.fix,
            "code_example": analysis.code_example,
            "confidence": analysis.confidence,
            "pip_install_hint": analysis.pip_install_hint,
            "is_beginner_mistake": analysis.is_beginner_mistake,
            "nearby_names": analysis.nearby_names,
            "smart_suggestions": analysis.smart_suggestions,
            "location": (
                {
                    "file": frame.file,
                    "line": frame.line_number,
                    "function": frame.function_name,
                    "source_snippet": frame.source_snippet,
                }
                if frame
                else None
            ),
        }
        typer.echo(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        render(parsed, analysis, lang=lang, console=_console)

    return True


def _read_file_or_run(source: Path) -> str:
    """
    Return traceback text from a source path.

    - .py files are executed via subprocess; stderr is returned.
    - All other files are read directly.
    """
    if source.suffix == ".py":
        import subprocess
        result = subprocess.run(
            [sys.executable, str(source)],
            capture_output=True,
            text=True,
        )
        return result.stderr or result.stdout or ""
    else:
        return source.read_text(encoding="utf-8", errors="replace")


# ─── Main command ─────────────────────────────────────────────────────────────

@app.command()
def main(
    source: Optional[Path] = typer.Argument(  # noqa: UP045
        None,
        help="Path to a .py script or .log/.txt traceback file.",
        exists=False,  # We validate manually for better messages
    ),
    paste: bool = typer.Option(
        False, "--paste", "-p",
        help="Read traceback from the system clipboard.",
    ),
    watch: bool = typer.Option(
        False, "--watch", "-w",
        help="Watch a .py file — re-analyse on every save.",
    ),
    lang: str = typer.Option(
        "en", "--lang", "-l",
        help="Output language: 'en' (default) or 'ar'.",
    ),
    as_json: bool = typer.Option(
        False, "--json",
        help="Output analysis as machine-readable JSON.",
    ),
    version: Optional[bool] = typer.Option(  # noqa: UP045
        None, "--version", "-v",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """
    [bold]fixpy[/bold] — Analyse a Python traceback and explain it in plain English.

    \b
    Examples:
      fixpy error.log
      fixpy app.py
      python app.py 2>&1 | fixpy
      fixpy --paste
      fixpy --watch app.py
      fixpy --lang ar error.log
    """
    s = get_strings(lang)

    # ── Arabic RTL note ───────────────────────────────────────────────────────
    if lang == "ar":
        _console.print(f"[dim]{s['lang_rtl_note']}[/dim]")

    # ── Watch mode ────────────────────────────────────────────────────────────
    if watch:
        if source is None:
            _err_console.print(
                "[red]Error:[/red] --watch requires a .py file argument.\n"
                "  Example: fixpy --watch app.py"
            )
            raise typer.Exit(1)

        target = Path(source)
        if not target.exists():
            _err_console.print(f"[red]Error:[/red] File not found: {target}")
            raise typer.Exit(1)

        _console.print(s["watch_start"].format(path=str(target)))

        def _on_change(text: str) -> None:
            _console.clear()
            _console.print(f"[dim]{s['watch_change']}[/dim]\n")
            if not text.strip():
                _console.print(f"[green]{s['watch_no_error']}[/green]")
                return
            found = _run_pipeline(text, lang=lang, as_json=as_json)
            if not found:
                _console.print(f"[green]{s['watch_no_error']}[/green]")

        watch_file(target, _on_change)
        return

    # ── Clipboard mode ────────────────────────────────────────────────────────
    if paste:
        text = read_clipboard()
        if not text:
            _err_console.print(f"[yellow]{s['paste_empty']}[/yellow]")
            raise typer.Exit(1)
        _run_pipeline(text, lang=lang, as_json=as_json)
        return

    # ── Piped stdin ───────────────────────────────────────────────────────────
    if not sys.stdin.isatty():
        text = sys.stdin.read()
        found = _run_pipeline(text, lang=lang, as_json=as_json)
        if not found:
            _err_console.print(f"[yellow]{s['no_traceback']}[/yellow]")
        return

    # ── File argument ─────────────────────────────────────────────────────────
    if source is not None:
        target = Path(source)
        if not target.exists():
            _err_console.print(f"[red]Error:[/red] File not found: {target}")
            raise typer.Exit(1)

        text = _read_file_or_run(target)
        found = _run_pipeline(text, lang=lang, as_json=as_json)
        if not found:
            _err_console.print(
                f"[yellow]{s['no_traceback']}[/yellow]\n"
                f"[dim]{s['pipe_hint']}[/dim]"
            )
        return

    # ── No input — show help ──────────────────────────────────────────────────
    _err_console.print(
        "[yellow]No input provided.[/yellow]\n"
        f"[dim]{s['pipe_hint']}[/dim]\n\n"
        "Run [bold]fixpy --help[/bold] for usage."
    )
    raise typer.Exit(1)


if __name__ == "__main__":
    app()
