"""
settings_tab.py
===============
Settings panel for the Hadith app.

Controls:
  ─ Appearance
    • Dark mode toggle  (warm dark palette, easy on eyes)
  ─ Reader — Arabic
    • Font family selector
    • Font size slider  (14 – 32)
    • Line spacing      (1.5 – 3.5)
  ─ Reader — English
    • Font family selector
    • Font size slider  (10 – 22)
    • Line spacing      (1.2 – 2.8)
  ─ Copy behaviour
    • Copy as plain text  (default ON) — strips all HTML / markdown before
      putting text into the clipboard
    • Copy as rich text   — copies with formatting intact
"""

import re
from PyQt6.QtWidgets import *
from PyQt6.QtCore    import Qt, pyqtSlot
from PyQt6.QtGui     import QFont, QFontDatabase

from settings_manager import Settings


# ─────────────────────────────────────────────────────────────────────────────
#  Plain-text clipboard filter
# ─────────────────────────────────────────────────────────────────────────────

def install_plain_copy_filter(app):
    """
    Installs a global event filter so that whenever the user copies (Ctrl+C)
    while plain_copy is enabled, the clipboard is stripped of HTML tags.
    Call once from main() after QApplication is created.
    """
    from PyQt6.QtCore   import QObject, QEvent
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui    import QKeySequence, QClipboard
    import html

    class PlainCopyFilter(QObject):
        def eventFilter(self, obj, event):
            # We intercept QClipboard::dataChanged instead of key events,
            # because Qt's rich-text widgets write HTML to the clipboard
            # before the event loop returns.
            return False   # passthrough; real work done in slot below

    _filter = PlainCopyFilter(app)
    app.installEventFilter(_filter)

    def _on_clipboard_changed():
        s = Settings.instance()
        if not s.plain_copy:
            return
        cb = QApplication.clipboard()
        if cb.mimeData().hasHtml():
            raw_html  = cb.mimeData().html()
            # strip tags and decode entities
            plain = re.sub(r"<[^>]+>", "", raw_html)
            plain = html.unescape(plain)
            # collapse excessive whitespace / newlines
            plain = re.sub(r"\n{3,}", "\n\n", plain)
            plain = re.sub(r"[ \t]+", " ",    plain)
            plain = plain.strip()
            # replace clipboard content silently
            cb.setText(plain, QClipboard.Mode.Clipboard)

    QApplication.clipboard().dataChanged.connect(_on_clipboard_changed)


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _section(title: str) -> QLabel:
    lbl = QLabel(title)
    lbl.setStyleSheet("""
        QLabel {
            font-size: 11px;
            font-weight: bold;
            color: #888888;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 18px 0 4px 0;
            background: transparent;
            border: none;
        }
    """)
    return lbl


def _label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setMinimumWidth(170)
    lbl.setStyleSheet("QLabel { font-size: 13px; background:transparent; border:none; }")
    return lbl


def _row(*widgets) -> QHBoxLayout:
    h = QHBoxLayout()
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(10)
    for w in widgets:
        if isinstance(w, int):
            h.addSpacing(w)
        else:
            h.addWidget(w)
    h.addStretch()
    return h


# ─────────────────────────────────────────────────────────────────────────────
#  Dark mode preview swatch
# ─────────────────────────────────────────────────────────────────────────────

class ColorSwatch(QWidget):
    def __init__(self, color: str, parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(22, 22)
        self.setStyleSheet(
            f"background:{color}; border:1px solid #aaa; border-radius:3px;")


# ─────────────────────────────────────────────────────────────────────────────
#  SettingsTab
# ─────────────────────────────────────────────────────────────────────────────

class SettingsTab(QWidget):

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self._s = Settings.instance()
        self._build()

    def _build(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # Centre-column scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        inner = QWidget()
        inner.setMaximumWidth(680)
        root  = QVBoxLayout(inner)
        root.setContentsMargins(40, 30, 40, 40)
        root.setSpacing(4)

        # ──────────────────────────────────────────────────────────────────────
        # Title
        title = QLabel("⚙️  الإعدادات  —  Settings")
        title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                padding-bottom: 8px;
                background: transparent;
                border: none;
            }
        """)
        root.addWidget(title)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color:#d0d0d0;")
        root.addWidget(sep)

        # ── Appearance ────────────────────────────────────────────────────────
        root.addWidget(_section("Appearance  /  المظهر"))

        # Dark mode
        dark_row = QHBoxLayout()
        dark_row.setContentsMargins(0, 0, 0, 0)
        dark_row.setSpacing(12)

        self._dark_toggle = self._make_toggle(
            "Dark Mode  —  الوضع الداكن",
            "Warm dark background, easy on the eyes in low light",
            self._s.dark_mode
        )
        dark_row.addLayout(self._dark_toggle["layout"])

        # palette swatches
        from settings_manager import Palette
        for key in ["reader_bg", "panel_bg", "section_bg", "reader_text"]:
            light_c = Palette.LIGHT[key]
            dark_c  = Palette.DARK[key]
            pair = QHBoxLayout()
            pair.setSpacing(2)
            pair.addWidget(ColorSwatch(light_c))
            pair.addWidget(ColorSwatch(dark_c))
            dark_row.addLayout(pair)

        dark_row.addStretch()
        root.addLayout(dark_row)

        self._dark_toggle["checkbox"].stateChanged.connect(self._on_dark_toggle)

        # ── Copy behaviour ────────────────────────────────────────────────────
        root.addWidget(_section("Copy Behaviour  /  نسخ النص"))

        self._copy_toggle = self._make_toggle(
            "Plain Text Copy  —  نسخ نص عادي",
            "When you copy text from the app, HTML formatting and markdown are "
            "stripped automatically. You get clean plain text.",
            self._s.plain_copy
        )
        root.addLayout(self._copy_toggle["layout"])
        self._copy_toggle["checkbox"].stateChanged.connect(self._on_copy_toggle)

        copy_note = QLabel(
            "تلقائياً عند النسخ يُزال كل تنسيق HTML / markdown ويُحفظ النص العادي فقط."
        )
        copy_note.setWordWrap(True)
        copy_note.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        copy_note.setStyleSheet(
            "QLabel { font-size:12px; color:#888; background:transparent; border:none; "
            "font-family:'Amiri','Traditional Arabic',Arial; padding:2px 0 0 28px; }")
        root.addWidget(copy_note)

        # ── Arabic reader ─────────────────────────────────────────────────────
        root.addWidget(_section("Arabic Text  /  النص العربي"))

        # Font family
        self._ar_font_combo = QComboBox()
        self._ar_font_combo.setObjectName("inputField")
        self._ar_font_combo.setFixedWidth(220)
        for f in ["Amiri", "Traditional Arabic", "Scheherazade New",
                  "Noto Naskh Arabic", "Noto Serif", "Arial", "Times New Roman"]:
            self._ar_font_combo.addItem(f)
        idx = self._ar_font_combo.findText(self._s.arabic_font)
        if idx >= 0: self._ar_font_combo.setCurrentIndex(idx)
        root.addLayout(_row(_label("Font Family  /  الخط"), self._ar_font_combo))
        self._ar_font_combo.currentTextChanged.connect(
            lambda t: setattr(self._s, "arabic_font", t))

        # Font size
        self._ar_size_slider, ar_size_lbl = self._make_slider(
            self._s.arabic_size, 14, 32, lambda v: f"{v}px")
        root.addLayout(_row(_label("Font Size  /  حجم الخط"),
                            self._ar_size_slider, ar_size_lbl))
        self._ar_size_slider.valueChanged.connect(
            lambda v: setattr(self._s, "arabic_size", v))

        # Line spacing
        ar_sp_vals  = [1.5, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.5]
        self._ar_spacing_combo = self._make_float_combo(
            ar_sp_vals, self._s.line_spacing_ar)
        root.addLayout(_row(_label("Line Spacing  /  تباعد الأسطر"),
                            self._ar_spacing_combo))
        self._ar_spacing_combo.currentIndexChanged.connect(
            lambda i: setattr(self._s, "line_spacing_ar", ar_sp_vals[i]))

        # ── English reader ────────────────────────────────────────────────────
        root.addWidget(_section("English Text  /  النص الإنجليزي"))

        self._en_font_combo = QComboBox()
        self._en_font_combo.setObjectName("inputField")
        self._en_font_combo.setFixedWidth(220)
        for f in ["Segoe UI", "Arial", "Georgia", "Palatino Linotype",
                  "Times New Roman", "Verdana", "Calibri"]:
            self._en_font_combo.addItem(f)
        idx2 = self._en_font_combo.findText(self._s.english_font)
        if idx2 >= 0: self._en_font_combo.setCurrentIndex(idx2)
        root.addLayout(_row(_label("Font Family"), self._en_font_combo))
        self._en_font_combo.currentTextChanged.connect(
            lambda t: setattr(self._s, "english_font", t))

        self._en_size_slider, en_size_lbl = self._make_slider(
            self._s.english_size, 10, 22, lambda v: f"{v}px")
        root.addLayout(_row(_label("Font Size"), self._en_size_slider, en_size_lbl))
        self._en_size_slider.valueChanged.connect(
            lambda v: setattr(self._s, "english_size", v))

        en_sp_vals  = [1.2, 1.4, 1.6, 1.8, 1.9, 2.0, 2.2, 2.4, 2.6, 2.8]
        self._en_spacing_combo = self._make_float_combo(
            en_sp_vals, self._s.line_spacing_en)
        root.addLayout(_row(_label("Line Spacing"), self._en_spacing_combo))
        self._en_spacing_combo.currentIndexChanged.connect(
            lambda i: setattr(self._s, "line_spacing_en", en_sp_vals[i]))

        # ── Reset ─────────────────────────────────────────────────────────────
        root.addSpacing(24)
        reset_btn = QPushButton("↺  Reset to Defaults  /  إعادة الضبط")
        reset_btn.setObjectName("actionButton")
        reset_btn.setFixedWidth(260)
        reset_btn.clicked.connect(self._reset)
        root.addWidget(reset_btn)

        root.addStretch()
        scroll.setWidget(inner)

        # centred layout
        outer.addStretch()
        outer.addWidget(scroll, 1)
        outer.addStretch()

    # ── Slot helpers ───────────────────────────────────────────────────────────

    def _on_dark_toggle(self, state):
        self._s.dark_mode = bool(state)
        self._apply_theme()

    def _on_copy_toggle(self, state):
        self._s.plain_copy = bool(state)

    def _apply_theme(self):
        """Push new stylesheet to the main window."""
        if hasattr(self.main_window, "setStyleSheet"):
            self.main_window.setStyleSheet(self._s.main_stylesheet())

    def _reset(self):
        self._s._dark_mode       = False
        self._s._arabic_font     = "Amiri"
        self._s._arabic_size     = 20
        self._s._english_font    = "Segoe UI"
        self._s._english_size    = 14
        self._s._plain_copy      = True
        self._s._line_spacing_ar = 2.4
        self._s._line_spacing_en = 1.9
        self._s.changed.emit()
        self._sync_controls()
        self._apply_theme()

    def _sync_controls(self):
        """Update all widgets to match current Settings values."""
        s = self._s
        self._dark_toggle["checkbox"].setChecked(s.dark_mode)
        self._copy_toggle["checkbox"].setChecked(s.plain_copy)

        idx = self._ar_font_combo.findText(s.arabic_font)
        if idx >= 0: self._ar_font_combo.setCurrentIndex(idx)
        self._ar_size_slider.setValue(s.arabic_size)

        idx2 = self._en_font_combo.findText(s.english_font)
        if idx2 >= 0: self._en_font_combo.setCurrentIndex(idx2)
        self._en_size_slider.setValue(s.english_size)

    # ── Widget factories ──────────────────────────────────────────────────────

    @staticmethod
    def _make_toggle(title: str, subtitle: str, checked: bool) -> dict:
        """Returns {"layout": QHBoxLayout, "checkbox": QCheckBox}"""
        cb = QCheckBox()
        cb.setChecked(checked)
        cb.setStyleSheet("""
            QCheckBox::indicator { width:20px; height:20px; }
            QCheckBox::indicator:checked  { background:#111; border:2px solid #111; border-radius:3px; }
            QCheckBox::indicator:unchecked { background:#fff; border:2px solid #aaa; border-radius:3px; }
        """)
        title_lbl    = QLabel(title)
        title_lbl.setStyleSheet(
            "QLabel{font-size:13px;font-weight:bold;background:transparent;border:none;}")
        subtitle_lbl = QLabel(subtitle)
        subtitle_lbl.setStyleSheet(
            "QLabel{font-size:11px;color:#888;background:transparent;border:none;}")
        texts = QVBoxLayout()
        texts.setSpacing(1)
        texts.setContentsMargins(0, 0, 0, 0)
        texts.addWidget(title_lbl)
        texts.addWidget(subtitle_lbl)

        row = QHBoxLayout()
        row.setContentsMargins(0, 4, 0, 4)
        row.setSpacing(12)
        row.addWidget(cb)
        row.addLayout(texts)
        row.addStretch()
        return {"layout": row, "checkbox": cb}

    @staticmethod
    def _make_slider(value: int, lo: int, hi: int, fmt) -> tuple:
        """Returns (QSlider, QLabel) with live value label."""
        sl = QSlider(Qt.Orientation.Horizontal)
        sl.setRange(lo, hi)
        sl.setValue(value)
        sl.setFixedWidth(180)
        sl.setStyleSheet("""
            QSlider::groove:horizontal { height:4px; background:#d0d0d0; border-radius:2px; }
            QSlider::handle:horizontal { width:14px; height:14px; margin:-5px 0;
                background:#333; border-radius:7px; }
            QSlider::sub-page:horizontal { background:#555; border-radius:2px; }
        """)
        lbl = QLabel(fmt(value))
        lbl.setFixedWidth(38)
        lbl.setStyleSheet(
            "QLabel{font-size:12px;color:#555;background:transparent;border:none;}")
        sl.valueChanged.connect(lambda v, l=lbl, f=fmt: l.setText(f(v)))
        return sl, lbl

    @staticmethod
    def _make_float_combo(values: list, current: float) -> QComboBox:
        cb = QComboBox()
        cb.setObjectName("inputField")
        cb.setFixedWidth(90)
        best = 0
        for i, v in enumerate(values):
            cb.addItem(f"{v:.1f}×")
            if abs(v - current) < 0.01:
                best = i
        cb.setCurrentIndex(best)
        return cb