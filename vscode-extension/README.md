# fixpy VS Code extension (preview)

This extension integrates the `fixpy` CLI into VS Code to provide:

- traceback detection in open text/log files
- quick analysis commands for selected/full traceback text
- beginner-friendly explanations and fix suggestions in an output panel
- inline diagnostics on traceback frame lines

## Requirements

- VS Code `1.85+`
- Python installed
- `fixpy` installed and available in your PATH:

```bash
pip install fixpy-traceback
```

## Commands

- `fixpy: Analyze Selected Traceback`
- `fixpy: Analyze Traceback in Current File`
- `fixpy: Copy Top Fix Suggestion`

## Settings

- `fixpy.command` (default: `fixpy`)
- `fixpy.language` (`en` or `ar`)
- `fixpy.autoDetectTracebacks` (default: `true`)
- `fixpy.maxBufferMB` (default: `5`)

## Local development

```bash
cd vscode-extension
npm install
# press F5 in VS Code to launch Extension Development Host
```
