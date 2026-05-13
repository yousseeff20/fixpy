"""
Rich-powered terminal formatter for fixpy.

Renders an Analysis as a polished, color-coded terminal report using Rich
panels, tables, syntax highlighting, and progress bars.

Design note:
    All rendering is pure functions (no class state) so they're trivially
    testable and composable. The Console is created fresh per render call
    to make output capturing in tests straightforward.
"""

from __future__ import annotations

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from ..i18n import get_strings
from ..models import Analysis, ParsedTraceback

# ─── Colour palette ───────────────────────────────────────────────────────────
C_ERROR = "bold red"
C_CAUSE = "bold yellow"
C_FIX = "bold green"
C_HINT = "cyan"
C_DIM = "dim white"
C_ACCENT = "bold magenta"
C_FILE = "bold blue"
C_BADGE = "bold white on dark_red"


def render(
    parsed: ParsedTraceback,
    analysis: Analysis,
    lang: str = "en",
    console: Console | None = None,
) -> None:
    """
    Render the full fixpy report to the terminal.

    Args:
        parsed:   The parsed traceback (for stack frames).
        analysis: The analysis result to display.
        lang:     Language code ('en' or 'ar').
        console:  Optional Rich Console — creates a new one if not given.
    """
    if console is None:
        console = Console(highlight=False)

    s = get_strings(lang)

    # ── Header ────────────────────────────────────────────────────────────────
    _render_header(console, s, analysis)

    # ── Error location ────────────────────────────────────────────────────────
    if parsed.frames:
        _render_location(console, s, parsed)

    # ── Cause ─────────────────────────────────────────────────────────────────
    _render_section(
        console,
        title=s["section_cause"],
        content=analysis.ar_cause if lang == "ar" else analysis.cause,
        style=C_CAUSE,
    )

    # ── Explanation ───────────────────────────────────────────────────────────
    _render_section(
        console,
        title=s["section_explain"],
        content=analysis.ar_explanation if lang == "ar" else analysis.explanation,
        style="white",
    )

    # ── Fix ───────────────────────────────────────────────────────────────────
    _render_section(
        console,
        title=s["section_fix"],
        content=analysis.ar_fix if lang == "ar" else analysis.fix,
        style=C_FIX,
    )

    # ── Code example ──────────────────────────────────────────────────────────
    if analysis.code_example:
        _render_code(console, s, analysis.code_example)

    # ── Stack walkthrough ─────────────────────────────────────────────────────
    if analysis.stack_explanation and len(parsed.frames) > 1:
        _render_stack(console, s, analysis.stack_explanation)

    # ── pip install hint ──────────────────────────────────────────────────────
    if analysis.pip_install_hint:
        _render_pip(console, s, analysis.pip_install_hint)

    # ── Nearby names ──────────────────────────────────────────────────────────
    if analysis.nearby_names:
        _render_nearby(console, s, analysis.nearby_names)

    # ── Smart suggestions ─────────────────────────────────────────────────────
    if analysis.smart_suggestions:
        _render_suggestions(console, s, analysis.smart_suggestions)

    # ── Confidence bar ────────────────────────────────────────────────────────
    _render_confidence(console, s, analysis.confidence)

    # ── Beginner badge ────────────────────────────────────────────────────────
    if analysis.is_beginner_mistake:
        console.print(
            f"\n  [{C_BADGE}] {s['beginner_badge']} [/{C_BADGE}]",
            justify="center",
        )

    console.print()


# ─── Section renderers ────────────────────────────────────────────────────────

def _render_header(console: Console, s: dict, analysis: Analysis) -> None:
    title = Text(s["header_title"], style="bold white")
    exc_badge = Text(f"  {analysis.exception_type}  ", style="bold white on red")

    header_text = Text.assemble(
        "\n  ",
        exc_badge,
        "  ",
        title,
        "\n",
    )
    console.print(
        Panel(
            header_text,
            box=box.DOUBLE_EDGE,
            border_style="red",
            padding=(0, 2),
        )
    )


def _render_location(console: Console, s: dict, parsed: ParsedTraceback) -> None:
    frame = parsed.frames[-1]  # innermost = most relevant
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column("label", style=C_DIM, no_wrap=True)
    table.add_column("value", style=C_FILE, no_wrap=False)

    table.add_row("File", frame.file)
    table.add_row("Line", str(frame.line_number))
    table.add_row("Function", frame.function_name)
    if frame.source_snippet:
        table.add_row("Code", f"[italic]{frame.source_snippet}[/italic]")

    console.print(
        Panel(table, title=f"[bold]{s['section_location']}[/bold]", border_style="blue")
    )


def _render_section(
    console: Console,
    title: str,
    content: str | None,
    style: str = "white",
) -> None:
    if not content:
        return
    console.print(
        Panel(
            Text(content, style=style),
            title=f"[bold]{title}[/bold]",
            border_style="bright_black",
            padding=(1, 2),
        )
    )


def _render_code(console: Console, s: dict, code: str) -> None:
    syntax = Syntax(
        code,
        "python",
        theme="monokai",
        line_numbers=False,
        word_wrap=True,
        padding=(1, 2),
    )
    console.print(
        Panel(
            syntax,
            title=f"[bold]{s['section_example']}[/bold]",
            border_style="green",
        )
    )


def _render_stack(console: Console, s: dict, steps: list[str]) -> None:
    table = Table(box=box.SIMPLE_HEAVY, show_header=False, padding=(0, 1))
    table.add_column("step", style=C_DIM, no_wrap=True, min_width=6)
    table.add_column("detail", style="white")

    for i, step in enumerate(steps, 1):
        table.add_row(f"[{C_HINT}]Step {i}[/{C_HINT}]", step)

    console.print(
        Panel(
            table,
            title=f"[bold]{s['section_stack']}[/bold]",
            border_style="bright_black",
        )
    )


def _render_pip(console: Console, s: dict, pip_cmd: str) -> None:
    code = Syntax(pip_cmd, "bash", theme="monokai", padding=(1, 2))
    console.print(
        Panel(
            code,
            title=f"[bold]{s['section_pip']}[/bold]",
            border_style="yellow",
        )
    )


def _render_nearby(console: Console, s: dict, names: list[str]) -> None:
    items = "  ".join(f"[bold cyan]{n}[/bold cyan]" for n in names)
    console.print(
        Panel(
            Text.from_markup(items),
            title=f"[bold]{s['section_nearby']}[/bold]",
            border_style="cyan",
            padding=(1, 2),
        )
    )


def _render_suggestions(console: Console, s: dict, tips: list[str]) -> None:
    lines = "\n".join(f"  [bold cyan]•[/bold cyan] {tip}" for tip in tips)
    console.print(
        Panel(
            Text.from_markup(lines),
            title=f"[bold]{s['section_suggest']}[/bold]",
            border_style="magenta",
            padding=(1, 2),
        )
    )


def _render_confidence(console: Console, s: dict, score: float) -> None:
    filled = int(score * 20)
    bar = "#" * filled + "-" * (20 - filled)
    pct = f"{score * 100:.0f}%"

    label = s["confidence_label"]
    note = s["confidence_note"]

    line = Text.from_markup(
        f"  {label}: [{C_HINT}]{bar}[/{C_HINT}] [bold]{pct}[/bold]"
        f"  [{C_DIM}]{note}[/{C_DIM}]"
    )
    console.print(Rule(style="bright_black"))
    console.print(line)
