"""
English string catalogue for fixpy.

Keys are used by the formatter; values are user-facing strings.
Keeping strings in one place makes future translation straightforward.
"""

STRINGS: dict[str, str] = {
    # Section headers
    "header_title": "fixpy -- Error Detected",
    "section_location": "[>>] Error Location",
    "section_cause": "[?] What Happened",
    "section_explain": "[i] Why It Happened",
    "section_fix": "[*] How to Fix It",
    "section_example": "[+] Fixed Code Example",
    "section_stack": "[~] Call Stack (step-by-step)",
    "section_suggest": "[!] Smart Suggestions",
    "section_nearby": "Did you mean...?",
    "section_pip": "[pkg] Missing Package",
    # Confidence
    "confidence_label": "Confidence",
    "confidence_note": "(pattern-based analysis -- not AI)",
    # Beginner badge
    "beginner_badge": "[Beginner Tip] Common Beginner Mistake",
    # Watch mode
    "watch_start": "Watching [bold]{path}[/bold] -- press Ctrl+C to stop.",
    "watch_change": "File changed, re-analysing...",
    "watch_no_error": "[OK] No traceback detected -- script ran successfully.",
    # General
    "no_traceback": "No Python traceback found in the input.",
    "pipe_hint": "Tip: pipe your script output:  python app.py 2>&1 | fixpy",
    "paste_empty": "Clipboard is empty or contains no traceback.",
    "lang_rtl_note": "Note: Arabic (RTL) rendering may vary by terminal.",
}
