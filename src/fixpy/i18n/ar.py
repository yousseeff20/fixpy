"""
Arabic string catalogue for fixpy (--lang ar).

Note: RTL rendering quality depends on the terminal emulator.
Windows Terminal and most Linux terminals support it reasonably well.
"""

STRINGS: dict[str, str] = {
    # Section headers
    "header_title": "fixpy -- تم اكتشاف خطأ",
    "section_location": "موقع الخطأ",
    "section_cause": "ماذا حدث",
    "section_explain": "لماذا حدث",
    "section_fix": "كيف تصلحه",
    "section_example": "مثال على الكود المصحح",
    "section_stack": "سلسلة الاستدعاءات (خطوة بخطوة)",
    "section_suggest": "اقتراحات ذكية",
    "section_nearby": "هل تقصد...؟",
    "section_pip": "حزمة مفقودة",
    # Confidence
    "confidence_label": "مستوى الثقة",
    "confidence_note": "(تحليل قائم على الأنماط -- ليس ذكاءً اصطناعياً)",
    # Beginner badge
    "beginner_badge": "[مبتدئ] خطأ شائع للمبتدئين",
    # Watch mode
    "watch_start": "مراقبة [bold]{path}[/bold] -- اضغط Ctrl+C للإيقاف.",
    "watch_change": "تم تعديل الملف، جارٍ إعادة التحليل...",
    "watch_no_error": "[OK] لم يتم اكتشاف أي خطأ -- نجح تشغيل السكريبت.",
    # General
    "no_traceback": "لم يتم اكتشاف أي traceback في المدخلات.",
    "pipe_hint": "نصيحة: مرّر مخرجات سكريبتك:  python app.py 2>&1 | fixpy",
    "paste_empty": "الحافظة فارغة أو لا تحتوي على traceback.",
    "lang_rtl_note": "ملاحظة: قد يختلف عرض النص العربي حسب نوع الطرفية.",
}
