"""
Traceback parser — converts raw Python traceback text into ParsedTraceback.

Design decisions:
  - Pure regex, no subprocess — handles text from any source (stdin, file, clipboard).
  - Handles standard tracebacks, SyntaxError (unique layout), and chained exceptions.
  - Graceful degradation: if parsing partially fails, returns best-effort result.
"""

from __future__ import annotations

import re

from ..models import ParsedTraceback, StackFrame

# ─── Regex patterns ───────────────────────────────────────────────────────────

# Standard traceback header
_HEADER = re.compile(r"Traceback \(most recent call last\):")

# Frame line: '  File "path.py", line 42, in function_name'
_FRAME = re.compile(
    r'^\s+File "(.+)", line (\d+), in (.+)$',
    re.MULTILINE,
)

# Source snippet: the line of code shown under a frame
_SNIPPET = re.compile(r"^( {4,})(.+)$", re.MULTILINE)

# Exception line: "ExceptionType: message"
_EXCEPTION_LINE = re.compile(
    r"^([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*Error|[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*Exception"
    r"|[A-Za-z_]\w*Warning|StopIteration|SystemExit|KeyboardInterrupt"
    r"|GeneratorExit|[A-Za-z_]\w*): (.*)$",
    re.MULTILINE,
)

# Loose fallback: any "Word: text" at start of a line
_EXCEPTION_LOOSE = re.compile(r"^([A-Za-z_]\w*): (.+)$", re.MULTILINE)

# Chained exception separators
_CHAINED = re.compile(
    r"(During handling of the above exception, another exception occurred:|"
    r"The above exception was the direct cause of the following exception:)",
)

# SyntaxError specific: "  File ..., line N" (no "in <func>")
_SYNTAX_FRAME = re.compile(r'^\s+File "(.+)", line (\d+)$', re.MULTILINE)


class TracebackParser:
    """
    Parses raw Python traceback text into a structured ParsedTraceback.

    Usage::

        parser = TracebackParser()
        parsed = parser.parse(raw_text)
        if parsed:
            # use parsed.exception_type, parsed.frames, etc.
    """

    def parse(self, text: str) -> ParsedTraceback | None:
        """
        Parse raw traceback text.

        Returns None if no recognisable traceback is found.
        """
        text = text.strip()
        if not text:
            return None

        # Split on chained exception markers
        chain_match = _CHAINED.search(text)
        if chain_match:
            return self._parse_chained(text, chain_match)

        return self._parse_single(text)

    # ─── Internal helpers ─────────────────────────────────────────────────────

    def _parse_single(self, text: str) -> ParsedTraceback | None:
        """Parse one (non-chained) traceback block."""
        exception_type, message = self._extract_exception(text)
        if not exception_type:
            return None

        frames = self._extract_frames(text, exception_type)

        return ParsedTraceback(
            exception_type=exception_type,
            message=message,
            frames=frames,
            raw_text=text,
            is_chained=False,
        )

    def _parse_chained(
        self, text: str, chain_match: re.Match
    ) -> ParsedTraceback:
        """Parse a chained exception — inner and outer blocks."""
        split_pos = chain_match.start()
        inner_text = text[:split_pos].strip()
        outer_text = text[chain_match.end() :].strip()

        inner = self._parse_single(inner_text)
        outer = self._parse_single(outer_text)

        if outer is None:
            return self._parse_single(text) or _empty(text)

        outer.is_chained = True
        outer.inner_exception = inner
        return outer

    def _extract_exception(self, text: str) -> tuple[str, str]:
        """
        Extract exception type and message from traceback text.

        Searches from the *end* of the text so the final exception line wins
        over any exceptions mentioned in the call stack.
        """
        # Try precise pattern first
        matches = list(_EXCEPTION_LINE.finditer(text))
        if matches:
            last = matches[-1]
            return last.group(1), last.group(2).strip()

        # Fallback: loose pattern
        matches = list(_EXCEPTION_LOOSE.finditer(text))
        if matches:
            last = matches[-1]
            return last.group(1), last.group(2).strip()

        return "", ""

    def _extract_frames(
        self, text: str, exception_type: str
    ) -> list[StackFrame]:
        """Extract all stack frames, with source snippets where available."""
        frames: list[StackFrame] = []

        # SyntaxError has a different frame format (no "in <func>")
        if exception_type in ("SyntaxError", "IndentationError", "TabError"):
            return self._extract_syntax_frames(text)

        lines = text.splitlines()
        i = 0
        while i < len(lines):
            frame_match = _FRAME.match(lines[i])
            if frame_match:
                file_path = frame_match.group(1)
                line_num = int(frame_match.group(2))
                func_name = frame_match.group(3).strip()

                # Next line(s) may be source snippets
                snippet: str | None = None
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    # Snippet lines are indented more than frame lines
                    if next_line.startswith("    ") and not _FRAME.match(
                        next_line
                    ):
                        snippet = next_line.strip()
                        i += 1  # consume snippet line

                frames.append(
                    StackFrame(
                        file=file_path,
                        line_number=line_num,
                        function_name=func_name,
                        source_snippet=snippet,
                    )
                )
            i += 1

        return frames

    def _extract_syntax_frames(self, text: str) -> list[StackFrame]:
        """SyntaxError-specific frame extraction."""
        frames: list[StackFrame] = []
        for m in _SYNTAX_FRAME.finditer(text):
            frames.append(
                StackFrame(
                    file=m.group(1),
                    line_number=int(m.group(2)),
                    function_name="<module>",
                    source_snippet=None,
                )
            )
        return frames


def _empty(raw: str) -> ParsedTraceback:
    """Return a minimal ParsedTraceback when parsing fully fails."""
    return ParsedTraceback(
        exception_type="UnknownError",
        message="Could not parse traceback",
        frames=[],
        raw_text=raw,
    )
