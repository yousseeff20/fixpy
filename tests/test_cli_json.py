"""CLI JSON output tests."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from fixpy.cli import app


runner = CliRunner()


def test_json_output_includes_location_for_traceback(tb_zero_division):
    result = runner.invoke(app, ["--json"], input=tb_zero_division)

    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    assert payload["exception_type"] == "ZeroDivisionError"
    assert payload["location"]["file"] == "app.py"
    assert payload["location"]["line"] == 5
    assert payload["location"]["function"] == "<module>"


def test_json_output_location_is_none_without_frames():
    traceback_text = "CustomError: oops\n"
    result = runner.invoke(app, ["--json"], input=traceback_text)

    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    assert payload["exception_type"] == "CustomError"
    assert payload["location"] is None
