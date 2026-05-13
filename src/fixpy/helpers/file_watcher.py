"""
File watcher — runs a Python script on each save and re-analyses its output.

Uses watchdog to monitor file-system events. When the watched file is
modified, the script is executed via subprocess and its combined stderr
(where Python tracebacks appear) is captured for analysis.

Architecture note:
    The watcher owns the event loop. The callback receives raw stderr text
    and is responsible for parsing + displaying — keeping concerns separated.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEventHandler  # type: ignore[import]
from watchdog.observers import Observer  # type: ignore[import]


class _ChangeHandler(FileSystemEventHandler):
    """Triggers *callback* whenever the watched file is modified."""

    def __init__(self, target: Path, callback: Callable[[str], None]) -> None:
        super().__init__()
        self._target = target.resolve()
        self._callback = callback
        self._last_run: float = 0.0
        self._debounce = 0.5  # seconds — avoid double-triggers on rapid saves

    def on_modified(self, event) -> None:  # type: ignore[override]
        if event.is_directory:
            return
        changed = Path(event.src_path).resolve()
        if changed != self._target:
            return
        now = time.monotonic()
        if now - self._last_run < self._debounce:
            return
        self._last_run = now
        self._callback(self._run_script())

    def _run_script(self) -> str:
        """Execute the watched Python script and return its stderr."""
        result = subprocess.run(
            [sys.executable, str(self._target)],
            capture_output=True,
            text=True,
        )
        # Python tracebacks go to stderr; also capture stdout for mixed output
        output = result.stderr or result.stdout or ""
        return output


def watch_file(
    path: Path,
    on_change: Callable[[str], None],
    initial_run: bool = True,
) -> None:
    """
    Watch *path* for changes and call *on_change* with the script's stderr.

    Blocks until the user interrupts with Ctrl-C.

    Args:
        path:        Path to the Python file to watch.
        on_change:   Callback receiving raw stderr/stdout text.
        initial_run: If True, run the script once immediately on start.
    """
    handler = _ChangeHandler(path, on_change)

    if initial_run:
        on_change(handler._run_script())

    observer = Observer()
    observer.schedule(handler, str(path.parent), recursive=False)
    observer.start()

    try:
        while observer.is_alive():
            observer.join(timeout=1)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
