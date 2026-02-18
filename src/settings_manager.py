"""
settings_manager.py
====================
Global settings singleton for the Hadith app.

Covers:
  - Dark mode (warm, easy-on-eye palette)
  - Arabic font family + size
  - English font family + size
  - Copy mode: plain text (strips HTML/markdown) vs rich text
  - Text colour overrides (light / dark)
  - Background colour
  - Search highlight colour

Usage:
    from settings_manager import Settings
    s = Settings.instance()
    s.changed.connect(my_slot)          # fires whenever any value changes
    dark = s.dark_mode
    s.dark_mode = True                  # triggers changed signal
"""

from PyQt6.QtCore  import QObject, pyqtSignal
from PyQt6.QtGui   import QFont, QColor


# ─────────────────────────────────────────────────────────────────────────────
#  Palette definitions
# ─────────────────────────────────────────────────────────────────────────────

class Palette:
    """
    Light palette  — clean white / monochrome Wikipedia-style
    Dark palette   — warm near-black (not blue-shifted), low contrast ratio
                     that's easy on eyes in dim environments.
    """

    LIGHT = dict(
        # reader area
        reader_bg        = "#ffffff",
        reader_text      = "#111111",
        reader_border    = "#dcdcdc",
        # panels / toolbar
        panel_bg         = "#f4f4f4",
        panel_border     = "#d0d0d0",
        panel_text       = "#222222",
        # section cards
        section_bg       = "#fafafa",
        section_border   = "#e0e0e0",
        section_title    = "#444444",
        # badge (hadith number)
        badge_bg         = "#ebebeb",
        badge_border     = "#c0c0c0",
        badge_text       = "#111111",
        # chapter bar
        chapter_bar_bg   = "#f7f7f7",
        # active button (current hadith / chapter)
        active_btn_bg    = "#111111",
        active_btn_text  = "#ffffff",
        # sidebar tree
        sidebar_bg       = "#f4f4f4",
        # highlights
        highlight_bg     = "#cc0000",
        highlight_text   = "#ffffff",
        # narrator label
        narrator_color   = "#555555",
        # scrollbar
        scrollbar        = "#cccccc",
    )

    DARK = dict(
        # Warm dark — background is a very dark warm grey (not pure black,
        # not blue-tinged). Text is a soft off-white. Very easy on eyes.
        reader_bg        = "#1c1a17",
        reader_text      = "#e8e2d9",
        reader_border    = "#3a3630",
        panel_bg         = "#242220",
        panel_border     = "#3a3630",
        panel_text       = "#d8d2c8",
        section_bg       = "#201e1b",
        section_border   = "#353028",
        section_title    = "#b0a898",
        badge_bg         = "#2e2b27",
        badge_border     = "#4a453e",
        badge_text       = "#e8e2d9",
        chapter_bar_bg   = "#242220",
        active_btn_bg    = "#c8b98a",   # warm gold — not harsh white
        active_btn_text  = "#1c1a17",
        sidebar_bg       = "#1e1c19",
        highlight_bg     = "#b84040",   # slightly muted red — less jarring in dark
        highlight_text   = "#ffffff",
        narrator_color   = "#9a9080",
        scrollbar        = "#4a453e",
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Settings singleton
# ─────────────────────────────────────────────────────────────────────────────

class Settings(QObject):
    """
    Singleton.  Emit `changed` whenever any property is set.
    Consumers connect to `changed` and re-apply styles.
    """
    changed = pyqtSignal()

    _instance = None

    @classmethod
    def instance(cls) -> "Settings":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        # ── defaults ─────────────────────────────────────────────────────────
        self._dark_mode        : bool  = False
        self._arabic_font      : str   = "Amiri"
        self._arabic_size      : int   = 20
        self._english_font     : str   = "Segoe UI"
        self._english_size     : int   = 14
        self._plain_copy       : bool  = True    # copy as plain text (no HTML)
        self._line_spacing_ar  : float = 2.4     # CSS line-height for Arabic
        self._line_spacing_en  : float = 1.9

    # ── properties ────────────────────────────────────────────────────────────

    @property
    def dark_mode(self) -> bool:        return self._dark_mode
    @dark_mode.setter
    def dark_mode(self, v: bool):
        if self._dark_mode != v:
            self._dark_mode = v; self.changed.emit()

    @property
    def arabic_font(self) -> str:       return self._arabic_font
    @arabic_font.setter
    def arabic_font(self, v: str):
        if self._arabic_font != v:
            self._arabic_font = v; self.changed.emit()

    @property
    def arabic_size(self) -> int:       return self._arabic_size
    @arabic_size.setter
    def arabic_size(self, v: int):
        if self._arabic_size != v:
            self._arabic_size = v; self.changed.emit()

    @property
    def english_font(self) -> str:      return self._english_font
    @english_font.setter
    def english_font(self, v: str):
        if self._english_font != v:
            self._english_font = v; self.changed.emit()

    @property
    def english_size(self) -> int:      return self._english_size
    @english_size.setter
    def english_size(self, v: int):
        if self._english_size != v:
            self._english_size = v; self.changed.emit()

    @property
    def plain_copy(self) -> bool:       return self._plain_copy
    @plain_copy.setter
    def plain_copy(self, v: bool):
        if self._plain_copy != v:
            self._plain_copy = v; self.changed.emit()

    @property
    def line_spacing_ar(self) -> float: return self._line_spacing_ar
    @line_spacing_ar.setter
    def line_spacing_ar(self, v: float):
        if self._line_spacing_ar != v:
            self._line_spacing_ar = v; self.changed.emit()

    @property
    def line_spacing_en(self) -> float: return self._line_spacing_en
    @line_spacing_en.setter
    def line_spacing_en(self, v: float):
        if self._line_spacing_en != v:
            self._line_spacing_en = v; self.changed.emit()

    # ── palette access ────────────────────────────────────────────────────────

    @property
    def palette(self) -> dict:
        return Palette.DARK if self._dark_mode else Palette.LIGHT

    def p(self, key: str) -> str:
        """Shorthand: Settings.instance().p('reader_bg')"""
        return self.palette[key]

    # ── stylesheet generators ─────────────────────────────────────────────────

    def main_stylesheet(self) -> str:
        """
        Full app stylesheet that replaces the one in main_window.py.
        Respects current dark/light palette.
        """
        p = self.palette
        return f"""
/* ── Main window ── */
QMainWindow, QDialog {{
    background: {p['panel_bg']};
    color: {p['panel_text']};
}}
QTabWidget::pane {{
    border: none;
    background: {p['panel_bg']};
}}
QTabBar::tab {{
    background: {p['panel_bg']};
    color: {p['panel_text']};
    padding: 8px 20px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 13px;
}}
QTabBar::tab:selected {{
    border-bottom: 2px solid {p['active_btn_bg']};
    font-weight: bold;
    color: {p['reader_text']};
}}
QTabBar::tab:hover {{
    background: {p['section_bg']};
}}

/* ── Panels ── */
QFrame#sidePanel {{
    background: {p['panel_bg']};
    border-right: 1px solid {p['panel_border']};
}}
QFrame#toolbar {{
    background: {p['panel_bg']};
    border-bottom: 1px solid {p['panel_border']};
}}

/* ── Labels ── */
QLabel#panelHeader {{
    font-size: 14px;
    font-weight: bold;
    color: {p['panel_text']};
    background: {p['panel_bg']};
    padding: 6px 12px;
    border-bottom: 1px solid {p['panel_border']};
}}
QLabel#sectionTitle {{
    font-size: 12px;
    font-weight: bold;
    color: {p['section_title']};
    background: transparent;
    border: none;
    padding: 0;
}}
QLabel#countLabel {{
    font-size: 11px;
    color: {p['section_title']};
    background: transparent;
    border: none;
}}

/* ── Cards ── */
QFrame#detailsSection {{
    background: {p['section_bg']};
    border: 1px solid {p['section_border']};
    border-radius: 3px;
}}

/* ── Inputs ── */
QLineEdit#inputField, QSpinBox#inputField, QComboBox#inputField {{
    background: {p['reader_bg']};
    color: {p['reader_text']};
    border: 1px solid {p['panel_border']};
    border-radius: 3px;
    padding: 3px 8px;
    font-size: 12px;
}}
QComboBox#methodCombo {{
    background: {p['reader_bg']};
    color: {p['reader_text']};
    border: 1px solid {p['panel_border']};
    border-radius: 3px;
    padding: 3px 8px;
    font-size: 12px;
}}

/* ── Buttons ── */
QPushButton#actionButton {{
    background: {p['panel_bg']};
    color: {p['panel_text']};
    border: 1px solid {p['panel_border']};
    border-radius: 3px;
    padding: 4px 10px;
    font-size: 12px;
}}
QPushButton#actionButton:hover {{
    background: {p['section_bg']};
    border-color: {p['section_title']};
}}
QPushButton#toolbarButton {{
    background: {p['panel_bg']};
    color: {p['panel_text']};
    border: 1px solid {p['panel_border']};
    border-radius: 2px;
    font-size: 11px;
}}
QPushButton#toolbarButton:hover {{
    background: {p['section_bg']};
}}

/* ── Tree ── */
QTreeWidget#chainList {{
    background: {p['sidebar_bg']};
    color: {p['panel_text']};
    border: none;
    outline: none;
}}
QTreeWidget#chainList::item:selected {{
    background: {p['active_btn_bg']};
    color: {p['active_btn_text']};
}}
QTreeWidget#chainList::item:hover {{
    background: {p['section_bg']};
}}

/* ── List ── */
QListWidget {{
    background: {p['sidebar_bg']};
    color: {p['panel_text']};
    border: none;
    outline: none;
}}
QListWidget::item:selected {{
    background: {p['active_btn_bg']};
    color: {p['active_btn_text']};
}}

/* ── Scrollbars ── */
QScrollBar:vertical {{
    background: {p['panel_bg']};
    width: 10px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {p['scrollbar']};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar:horizontal {{
    background: {p['panel_bg']};
    height: 8px;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {p['scrollbar']};
    border-radius: 3px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}

/* ── Splitter ── */
QSplitter::handle {{
    background: {p['panel_border']};
}}
"""