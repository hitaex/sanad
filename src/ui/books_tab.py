"""
Books tab — Shamela-style hadith book viewer.

Exact JSON structure per file:
  {
    "metadata": {
      "length": N,
      "arabic":  { "title": "...", "author": "...", "introduction": "..." },
      "english": { "title": "...", "author": "...", "introduction": "..." }
    },
    "hadiths": [
      {
        "id": N, "idInBook": N, "chapterId": N, "bookId": N,
        "arabic": "full text including sanad...",
        "english": { "narrator": "...", "text": "..." }
      }, ...
    ],
    "chapter": { "id": N, "bookId": N, "arabic": "...", "english": "..." }
  }

Folder layout:
  Data/BOOKS/
    <category>/          ← e.g. "the_9_books", "forties"
      <book_folder>/     ← e.g. "bukhari", "nawawi40"
        1.json
        2.json
        introduction.json
        ...

UI flow:
  Sidebar tree  →  Book  →  Chapter tab bar  →  Single hadith view (one at a time)

Search scopes:
  1. Current page (current chapter)
  2. Whole book
  3. In a hadith (current hadith only)

Highlights all query matches in bright red inline.
"""

import os
import re
import json
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

BOOKS_ROOT = "Data/BOOKS"


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _chapter_sort_key(fname):
    """Sort chapter files: introduction first, then numerically."""
    stem = os.path.splitext(fname)[0]
    if stem == "introduction":
        return (0, 0, "")
    digits = re.sub(r"[^0-9]", "", stem)
    suffix = re.sub(r"[0-9]", "", stem)
    return (1, int(digits) if digits else 999, suffix)


def find_books():
    """
    Returns:
      { category: { book_folder_name: { "path": str, "chapters": [abs_path, ...] } } }
    """
    result = {}
    if not os.path.exists(BOOKS_ROOT):
        return result

    for cat in sorted(os.listdir(BOOKS_ROOT)):
        cat_path = os.path.join(BOOKS_ROOT, cat)
        if not os.path.isdir(cat_path):
            continue
        result[cat] = {}

        for book in sorted(os.listdir(cat_path)):
            book_path = os.path.join(cat_path, book)
            if not os.path.isdir(book_path):
                continue
            files = sorted(
                [f for f in os.listdir(book_path) if f.endswith(".json")],
                key=_chapter_sort_key
            )
            if files:
                result[cat][book] = {
                    "path":     book_path,
                    "chapters": [os.path.join(book_path, f) for f in files],
                }
    return result


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Books] {path}: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
#  Background book loader
# ─────────────────────────────────────────────────────────────────────────────

class BookLoader(QThread):
    """Load all chapter JSON files for one book in background."""
    done = pyqtSignal(list)   # list of chapter dicts

    def __init__(self, paths):
        super().__init__()
        self._paths = paths

    def run(self):
        chapters = []
        for p in self._paths:
            d = load_json(p)
            if d:
                chapters.append(d)
        self.done.emit(chapters)


# ─────────────────────────────────────────────────────────────────────────────
#  Red highlight engine
# ─────────────────────────────────────────────────────────────────────────────

def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def highlight(text: str, query: str) -> str:
    """
    Return HTML with every occurrence of query wrapped in a bright-red span.
    Case-insensitive match; preserves original casing in output.
    """
    if not query or not text:
        return _esc(text)

    parts = []
    lo_text  = text.lower()
    lo_query = query.lower()
    i = 0
    while True:
        p = lo_text.find(lo_query, i)
        if p == -1:
            parts.append(_esc(text[i:]))
            break
        parts.append(_esc(text[i:p]))
        parts.append(
            f'<span style="background:#cc0000;color:#ffffff;'
            f'font-weight:bold;border-radius:2px;padding:0 2px;">'
            f'{_esc(text[p:p+len(query)])}</span>'
        )
        i = p + len(query)
    return "".join(parts)


def hadith_has_match(h: dict, q: str) -> bool:
    if not q:
        return False
    ql = q.lower()
    arabic = (h.get("arabic", "") or "").lower()
    eng    = h.get("english", {})
    et     = ((eng.get("text",     "") if isinstance(eng, dict) else str(eng)) or "").lower()
    en_    = ((eng.get("narrator", "") if isinstance(eng, dict) else "")       or "").lower()
    return ql in arabic or ql in et or ql in en_


# ─────────────────────────────────────────────────────────────────────────────
#  Single-hadith viewer
# ─────────────────────────────────────────────────────────────────────────────

class HadithViewer(QWidget):
    """
    Displays ONE hadith at a time.
    Navigation bar: ◀ prev | ▶ next | spinbox jump | sliding number buttons.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hadiths: list = []
        self._current: int  = 0
        self._query:   str  = ""
        self._build()

    # ── build ─────────────────────────────────────────────────────────────

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Nav bar ───────────────────────────────────────────────────────
        nav = QFrame()
        nav.setObjectName("toolbar")
        nav.setFixedHeight(44)
        nl = QHBoxLayout(nav)
        nl.setContentsMargins(10, 4, 10, 4)
        nl.setSpacing(6)
        nav.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._prev_btn = QPushButton("◀  السابق")
        self._prev_btn.setObjectName("actionButton")
        self._prev_btn.setFixedWidth(100)
        self._prev_btn.clicked.connect(lambda: self._go(self._current - 1))

        self._next_btn = QPushButton("التالي  ▶")
        self._next_btn.setObjectName("actionButton")
        self._next_btn.setFixedWidth(100)
        self._next_btn.clicked.connect(lambda: self._go(self._current + 1))

        sep = QLabel("|")
        sep.setStyleSheet("color:#bbb; margin:0 4px;")

        lbl_jump = QLabel("انتقل إلى رقم:")
        lbl_jump.setObjectName("countLabel")

        self._spin = QSpinBox()
        self._spin.setRange(1, 1)
        self._spin.setFixedWidth(80)
        self._spin.setObjectName("inputField")
        self._spin.editingFinished.connect(lambda: self._go(self._spin.value() - 1))

        self._pos_lbl = QLabel("- / -")
        self._pos_lbl.setObjectName("countLabel")
        self._pos_lbl.setFixedWidth(70)
        self._pos_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for w in [self._prev_btn, self._next_btn, sep, lbl_jump,
                  self._spin, self._pos_lbl]:
            nl.addWidget(w)
        nl.addStretch()

        # ── Number buttons row ─────────────────────────────────────────────
        nbf = QFrame()
        nbf.setObjectName("toolbar")
        nbf.setFixedHeight(38)
        nbl = QHBoxLayout(nbf)
        nbl.setContentsMargins(10, 3, 10, 3)
        nbl.setSpacing(3)
        nbf.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self._num_btns: list[QPushButton] = []
        for _ in range(20):
            btn = QPushButton("")
            btn.setObjectName("toolbarButton")
            btn.setFixedSize(36, 28)
            btn.setVisible(False)
            nbl.addWidget(btn)
            self._num_btns.append(btn)
        nbl.addStretch()

        root.addWidget(nav)
        root.addWidget(nbf)

        # ── Scroll area ────────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: #ffffff; }")
        self._scroll = scroll

        container = QWidget()
        container.setStyleSheet("background:#ffffff;")
        cl = QVBoxLayout(container)
        cl.setContentsMargins(28, 22, 28, 28)
        cl.setSpacing(16)

        # Badge row
        br = QHBoxLayout()
        self._badge = QLabel("")
        self._badge.setStyleSheet("""
            QLabel {
                background: #ebebeb;
                color: #111111;
                font-family: 'Amiri', 'Traditional Arabic', Arial;
                font-size: 13px;
                font-weight: bold;
                padding: 4px 18px;
                border: 1px solid #c0c0c0;
                border-radius: 3px;
            }
        """)
        br.addWidget(self._badge)
        br.addStretch()
        cl.addLayout(br)

        # Arabic text section  (includes full sanad + matn)
        ar_frame = QFrame()
        ar_frame.setObjectName("detailsSection")
        arl = QVBoxLayout(ar_frame)
        arl.setContentsMargins(16, 12, 16, 12)
        arl.setSpacing(6)

        ar_title = QLabel("نص الحديث")
        ar_title.setObjectName("sectionTitle")
        arl.addWidget(ar_title)

        self._ar_lbl = QLabel()
        self._ar_lbl.setWordWrap(True)
        self._ar_lbl.setTextFormat(Qt.TextFormat.RichText)
        self._ar_lbl.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._ar_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self._ar_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._ar_lbl.setStyleSheet("""
            QLabel {
                font-family: 'Amiri', 'Traditional Arabic', 'Scheherazade New', serif;
                font-size: 20px;
                color: #000000;
                line-height: 2.4;
                background: transparent;
                border: none;
                padding: 6px 2px;
            }
        """)
        arl.addWidget(self._ar_lbl)
        cl.addWidget(ar_frame)

        # English section
        self._en_frame = QFrame()
        self._en_frame.setObjectName("detailsSection")
        enl = QVBoxLayout(self._en_frame)
        enl.setContentsMargins(16, 12, 16, 12)
        enl.setSpacing(5)

        en_title = QLabel("الترجمة الإنجليزية")
        en_title.setObjectName("sectionTitle")
        enl.addWidget(en_title)

        self._narr_lbl = QLabel()
        self._narr_lbl.setObjectName("countLabel")
        self._narr_lbl.setStyleSheet(
            "font-style:italic; color:#555; font-size:11px; background:transparent; border:none;")
        self._narr_lbl.setTextFormat(Qt.TextFormat.RichText)
        enl.addWidget(self._narr_lbl)

        self._en_lbl = QLabel()
        self._en_lbl.setWordWrap(True)
        self._en_lbl.setTextFormat(Qt.TextFormat.RichText)
        self._en_lbl.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self._en_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._en_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._en_lbl.setStyleSheet("""
            QLabel {
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
                color: #111111;
                line-height: 1.9;
                background: transparent;
                border: none;
                padding: 4px 2px;
            }
        """)
        enl.addWidget(self._en_lbl)
        cl.addWidget(self._en_frame)

        # Grade / reference meta
        self._meta_frame = QFrame()
        self._meta_frame.setObjectName("detailsSection")
        ml = QHBoxLayout(self._meta_frame)
        ml.setContentsMargins(16, 8, 16, 8)
        self._grade_lbl = QLabel()
        self._grade_lbl.setObjectName("countLabel")
        self._ref_lbl = QLabel()
        self._ref_lbl.setObjectName("countLabel")
        self._ref_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        ml.addWidget(self._grade_lbl)
        ml.addStretch()
        ml.addWidget(self._ref_lbl)
        cl.addWidget(self._meta_frame)

        cl.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll, 1)

    # ── Public API ────────────────────────────────────────────────────────

    def load_hadiths(self, hadiths: list, query: str = ""):
        self._hadiths = hadiths
        self._query   = query
        self._current = 0
        n = len(hadiths)
        self._spin.setRange(1, max(n, 1))
        self._pos_lbl.setText(f"1 / {n}" if n else "- / -")
        self._rebuild_num_btns()
        if hadiths:
            self._render(0)
        else:
            self._clear()

    def set_query(self, q: str):
        self._query = q
        if self._hadiths:
            self._render(self._current)

    def jump_to_index(self, idx: int):
        self._go(idx)

    # ── Navigation ────────────────────────────────────────────────────────

    def _go(self, idx: int):
        if not self._hadiths:
            return
        idx = max(0, min(idx, len(self._hadiths) - 1))
        self._current = idx
        self._spin.setValue(idx + 1)
        self._pos_lbl.setText(f"{idx + 1} / {len(self._hadiths)}")
        self._render(idx)
        self._rebuild_num_btns()
        self._scroll.verticalScrollBar().setValue(0)

    def _rebuild_num_btns(self):
        total = len(self._hadiths)
        cur   = self._current
        start = max(0, min(cur - 10, total - 20))

        for i, btn in enumerate(self._num_btns):
            idx = start + i
            if idx < total:
                h   = self._hadiths[idx]
                num = str(h.get("idInBook", idx + 1))
                btn.setText(num)
                btn.setVisible(True)
                try:
                    btn.clicked.disconnect()
                except TypeError:
                    pass
                cap = idx
                btn.clicked.connect(lambda _, x=cap: self._go(x))

                if idx == cur:
                    btn.setStyleSheet("""
                        QPushButton {
                            background: #111111;
                            color: #ffffff;
                            border: 1px solid #111111;
                            font-weight: bold;
                            border-radius: 2px;
                        }
                    """)
                else:
                    btn.setStyleSheet("")
            else:
                btn.setVisible(False)

    # ── Render ────────────────────────────────────────────────────────────

    def _render(self, idx: int):
        h = self._hadiths[idx]
        q = self._query

        num = h.get("idInBook", idx + 1)
        self._badge.setText(f"   الحديث رقم  {num}   ")

        # Arabic — the full text (sanad + matn together as Shamela shows it)
        arabic = h.get("arabic", "") or ""
        ar_html = (
            f'<div dir="rtl" style="font-family:Amiri,\'Traditional Arabic\',serif;'
            f'font-size:20px;line-height:2.4;color:#000;">'
            f'{highlight(arabic, q)}'
            f'</div>'
        )
        self._ar_lbl.setText(ar_html)

        # English
        eng  = h.get("english", {})
        et   = (eng.get("text",     "") if isinstance(eng, dict) else str(eng)) or ""
        narr = (eng.get("narrator", "") if isinstance(eng, dict) else "")        or ""

        if et:
            self._en_frame.setVisible(True)
            en_html = (
                f'<div style="font-family:\'Segoe UI\',Arial;font-size:14px;'
                f'line-height:1.9;color:#111;">'
                f'{highlight(et, q)}'
                f'</div>'
            )
            self._en_lbl.setText(en_html)

            if narr:
                self._narr_lbl.setText(
                    f'<i style="color:#555;font-size:11px;">'
                    f'Narrated by: {highlight(narr, q)}</i>'
                )
                self._narr_lbl.setVisible(True)
            else:
                self._narr_lbl.setVisible(False)
        else:
            self._en_frame.setVisible(False)

        grade = h.get("grade", "") or h.get("grade_ar", "") or ""
        ref   = h.get("reference", "") or h.get("source", "") or ""
        self._grade_lbl.setText(f"الدرجة: {grade}" if grade else "")
        self._ref_lbl.setText(f"المرجع: {ref}"    if ref   else "")
        self._meta_frame.setVisible(bool(grade or ref))

        self._prev_btn.setEnabled(idx > 0)
        self._next_btn.setEnabled(idx < len(self._hadiths) - 1)

    def _clear(self):
        self._badge.setText("")
        self._ar_lbl.setText("")
        self._en_lbl.setText("")
        self._narr_lbl.setText("")
        self._grade_lbl.setText("")
        self._ref_lbl.setText("")
        self._pos_lbl.setText("- / -")
        self._en_frame.setVisible(False)
        self._meta_frame.setVisible(False)
        for b in self._num_btns:
            b.setVisible(False)


# ─────────────────────────────────────────────────────────────────────────────
#  Chapter tab bar  (horizontal scrollable buttons)
# ─────────────────────────────────────────────────────────────────────────────

class ChapterBar(QScrollArea):
    """
    Scrollable row of chapter buttons.
    Each button shows the Arabic chapter name.
    Emits chapter_selected(int) with the chapter index.
    """
    chapter_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                border-bottom: 1px solid #d0d0d0;
                background: #f7f7f7;
            }
            QScrollBar:horizontal { height: 6px; }
        """)

        self._inner = QWidget()
        self._inner.setStyleSheet("background: #f7f7f7;")
        self._il = QHBoxLayout(self._inner)
        self._il.setContentsMargins(6, 6, 6, 6)
        self._il.setSpacing(4)
        self._inner.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._il.addStretch()
        self.setWidget(self._inner)

        self._btns:    list[QPushButton] = []
        self._current: int               = -1

    def load_chapters(self, chapters: list):
        """chapters: list of {"arabic": str, "english": str}"""
        # Clear
        while self._il.count() > 1:
            item = self._il.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._btns.clear()
        self._current = -1

        for i, ch in enumerate(chapters):
            label = ch.get("arabic") or ch.get("english") or f"باب {i + 1}"
            btn = QPushButton(label)
            btn.setObjectName("toolbarButton")
            btn.setCheckable(True)
            btn.setFixedHeight(30)
            btn.setMinimumWidth(70)
            cap = i
            btn.clicked.connect(lambda _, x=cap: self._select(x))
            self._il.insertWidget(self._il.count() - 1, btn)
            self._btns.append(btn)

        if self._btns:
            self._select(0)

    def select_silent(self, idx: int):
        """Select chapter without emitting signal (used when jumping from search)."""
        if 0 <= self._current < len(self._btns):
            self._btns[self._current].setChecked(False)
            self._btns[self._current].setStyleSheet("")
        self._current = idx
        if 0 <= idx < len(self._btns):
            self._btns[idx].setChecked(True)
            self._btns[idx].setStyleSheet(
                "QPushButton{background:#111;color:#fff;"
                "border:1px solid #111;font-weight:bold;}")
            QTimer.singleShot(0, lambda: self.ensureWidgetVisible(self._btns[idx]))

    def _select(self, idx: int):
        self.select_silent(idx)
        self.chapter_selected.emit(idx)


# ─────────────────────────────────────────────────────────────────────────────
#  Search results panel
# ─────────────────────────────────────────────────────────────────────────────

class SearchPanel(QWidget):
    """
    Shows clickable cards for every matching hadith.
    Emits jumped(chapter_idx, hadith_idx_in_chapter) when a card is clicked.
    """
    jumped = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._cnt_lbl = QLabel("")
        self._cnt_lbl.setObjectName("countLabel")
        self._cnt_lbl.setContentsMargins(14, 6, 14, 6)
        root.addWidget(self._cnt_lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea{border:none;background:#fff;}")

        self._inner = QWidget()
        self._inner.setStyleSheet("background:#fff;")
        self._il = QVBoxLayout(self._inner)
        self._il.setContentsMargins(12, 10, 12, 10)
        self._il.setSpacing(8)
        self._il.addStretch()
        scroll.setWidget(self._inner)
        root.addWidget(scroll, 1)

    def show_results(self, results: list, query: str):
        """results: list of (chapter_idx, hadith_idx, hadith_dict, chapter_label)"""
        while self._il.count() > 1:
            item = self._il.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        n = len(results)
        if n:
            self._cnt_lbl.setText(f"نتائج البحث:  {n}  حديث — انقر لفتح")
        else:
            self._cnt_lbl.setText("لا توجد نتائج")

        for ci, hi, h, ch_label in results:
            card = self._make_card(ci, hi, h, ch_label, query)
            self._il.insertWidget(self._il.count() - 1, card)

    def _make_card(self, ci, hi, h, ch_label, query):
        frame = QFrame()
        frame.setObjectName("detailsSection")
        frame.setCursor(Qt.CursorShape.PointingHandCursor)
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(12, 10, 12, 10)
        fl.setSpacing(5)

        # Top row: hadith number + chapter name
        top = QHBoxLayout()
        top.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        num_badge = QLabel(f"الحديث رقم {h.get('idInBook', '?')}")
        num_badge.setStyleSheet("""
            QLabel {
                background:#ebebeb; color:#111;
                font-family:'Amiri','Traditional Arabic',Arial;
                font-size:12px; font-weight:bold;
                padding:2px 10px; border:1px solid #c0c0c0; border-radius:2px;
            }
        """)
        ch_badge = QLabel(ch_label)
        ch_badge.setStyleSheet("""
            QLabel {
                background:#222; color:#fff;
                font-family:'Amiri','Traditional Arabic',Arial;
                font-size:11px;
                padding:2px 8px; border-radius:2px;
            }
        """)
        top.addWidget(num_badge)
        top.addWidget(ch_badge)
        top.addStretch()
        fl.addLayout(top)

        # Arabic snippet
        arabic = h.get("arabic", "") or ""
        snip_ar = arabic[:200] + ("…" if len(arabic) > 200 else "")
        ar_lbl = QLabel(
            f'<div dir="rtl" style="font-family:Amiri,\'Traditional Arabic\',serif;'
            f'font-size:16px;line-height:2.2;color:#000;">'
            f'{highlight(snip_ar, query)}</div>'
        )
        ar_lbl.setWordWrap(True)
        ar_lbl.setTextFormat(Qt.TextFormat.RichText)
        ar_lbl.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        ar_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        fl.addWidget(ar_lbl)

        # English snippet
        eng = h.get("english", {})
        et  = (eng.get("text", "") if isinstance(eng, dict) else str(eng)) or ""
        if et:
            snip_en = et[:130] + ("…" if len(et) > 130 else "")
            en_lbl = QLabel(
                f'<span style="font-size:12px;color:#444;">'
                f'{highlight(snip_en, query)}</span>'
            )
            en_lbl.setWordWrap(True)
            en_lbl.setTextFormat(Qt.TextFormat.RichText)
            fl.addWidget(en_lbl)

        cap_ci, cap_hi = ci, hi
        frame.mousePressEvent = lambda _, a=cap_ci, b=cap_hi: self.jumped.emit(a, b)
        return frame


# ─────────────────────────────────────────────────────────────────────────────
#  Book reader pane
# ─────────────────────────────────────────────────────────────────────────────

class BookReaderPane(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._chapters:    list = []   # loaded chapter dicts
        self._cur_ch:      int  = 0
        self._loader       = None
        self._search_mode: bool = False
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────
        hdr = QFrame()
        hdr.setObjectName("sidePanel")
        hdr.setFixedHeight(64)
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(16, 8, 16, 8)
        hdr.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        tc = QVBoxLayout()
        self._title_lbl = QLabel("اختر كتاباً من القائمة")
        self._title_lbl.setStyleSheet("""
            QLabel { font-family:'Amiri','Traditional Arabic',Arial;
                     font-size:17px; font-weight:bold; color:#000;
                     background:transparent; border:none; padding:0; }
        """)
        self._author_lbl = QLabel("")
        self._author_lbl.setStyleSheet("""
            QLabel { font-family:'Amiri','Traditional Arabic',Arial;
                     font-size:12px; color:#555;
                     background:transparent; border:none; padding:0; }
        """)
        tc.addWidget(self._title_lbl)
        tc.addWidget(self._author_lbl)
        hl.addLayout(tc)
        hl.addStretch()

        self._count_lbl = QLabel("")
        self._count_lbl.setObjectName("countLabel")
        hl.addWidget(self._count_lbl)

        self._loading_lbl = QLabel("⏳  جارٍ التحميل...")
        self._loading_lbl.setObjectName("countLabel")
        self._loading_lbl.setVisible(False)
        hl.addWidget(self._loading_lbl)

        root.addWidget(hdr)

        # ── Search bar ────────────────────────────────────────────────────
        sf = QFrame()
        sf.setObjectName("toolbar")
        sf.setFixedHeight(40)
        sl = QHBoxLayout(sf)
        sl.setContentsMargins(10, 4, 10, 4)
        sl.setSpacing(6)
        sf.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        # Scope selector
        self._scope = QComboBox()
        self._scope.setObjectName("methodCombo")
        self._scope.addItems([
            "في الباب الحالي",   # 0
            "في الكتاب كله",     # 1
            "في الحديث الحالي",  # 2
        ])
        self._scope.setFixedWidth(160)
        sl.addWidget(self._scope)

        self._search_box = QLineEdit()
        self._search_box.setPlaceholderText("🔍  بحث في الأحاديث (عربي / إنجليزي)...")
        self._search_box.setObjectName("inputField")
        self._search_box.textChanged.connect(self._on_search)
        sl.addWidget(self._search_box, 1)

        clr_btn = QPushButton("مسح")
        clr_btn.setObjectName("actionButton")
        clr_btn.setFixedWidth(55)
        clr_btn.clicked.connect(self._clear_search)
        sl.addWidget(clr_btn)

        root.addWidget(sf)

        # ── Chapter tab bar ───────────────────────────────────────────────
        self._ch_bar = ChapterBar()
        self._ch_bar.chapter_selected.connect(self._on_chapter)
        root.addWidget(self._ch_bar)

        # ── Stack: viewer | search results ────────────────────────────────
        self._stack = QStackedWidget()
        self._viewer = HadithViewer()
        self._stack.addWidget(self._viewer)        # index 0

        self._search_panel = SearchPanel()
        self._search_panel.jumped.connect(self._jump_from_search)
        self._stack.addWidget(self._search_panel)  # index 1

        root.addWidget(self._stack, 1)

    # ── Public ────────────────────────────────────────────────────────────

    def start_load(self, chapter_paths: list, meta: dict):
        if self._loader and self._loader.isRunning():
            self._loader.quit()
            self._loader.wait()

        self._chapters    = []
        self._cur_ch      = 0
        self._search_mode = False

        self._loading_lbl.setVisible(True)
        self._count_lbl.setText("")
        self._ch_bar.load_chapters([])
        self._viewer.load_hadiths([])
        self._stack.setCurrentIndex(0)
        self._search_box.blockSignals(True)
        self._search_box.clear()
        self._search_box.blockSignals(False)

        ar = meta.get("arabic",  {})
        en = meta.get("english", {})
        self._title_lbl.setText(ar.get("title")  or en.get("title")  or "جارٍ التحميل...")
        self._author_lbl.setText(ar.get("author") or en.get("author") or "")

        self._loader = BookLoader(chapter_paths)
        self._loader.done.connect(self._on_loaded)
        self._loader.start()

    # ── Slots ─────────────────────────────────────────────────────────────

    @pyqtSlot(list)
    def _on_loaded(self, chapters: list):
        self._loading_lbl.setVisible(False)
        self._chapters = chapters
        if not chapters:
            return

        total_h = sum(len(c.get("hadiths", [])) for c in chapters)
        self._count_lbl.setText(f"الأحاديث: {total_h}")

        # Build chapter label list for the bar
        labels = []
        for c in chapters:
            ch_obj = c.get("chapter", {})
            labels.append({
                "arabic":  ch_obj.get("arabic",  "") or "",
                "english": ch_obj.get("english", "") or "",
            })
        self._ch_bar.load_chapters(labels)
        # _on_chapter(0) fires automatically via load_chapters → _select(0)

    def _on_chapter(self, idx: int):
        if idx < 0 or idx >= len(self._chapters):
            return
        self._cur_ch = idx
        if not self._search_mode:
            hadiths = self._chapters[idx].get("hadiths", [])
            self._viewer.load_hadiths(hadiths, self._search_box.text().strip())
            self._stack.setCurrentIndex(0)

    def _on_search(self, text: str):
        text = text.strip()
        if not text:
            self._clear_search()
            return

        self._search_mode = True
        scope = self._scope.currentIndex()

        if scope == 2:
            # Current hadith only — just highlight in viewer, no results panel
            self._viewer.set_query(text)
            self._stack.setCurrentIndex(0)
            return

        if scope == 1:
            # Whole book
            pool = [
                (ci, hi, h,
                 (self._chapters[ci].get("chapter", {}).get("arabic", "") or
                  self._chapters[ci].get("chapter", {}).get("english", "") or
                  f"باب {ci + 1}"))
                for ci, c in enumerate(self._chapters)
                for hi, h in enumerate(c.get("hadiths", []))
            ]
        else:
            # Current chapter (scope == 0)
            ci = self._cur_ch
            if not self._chapters:
                return
            ch_label = (self._chapters[ci].get("chapter", {}).get("arabic", "") or
                        self._chapters[ci].get("chapter", {}).get("english", "") or
                        f"باب {ci + 1}")
            pool = [
                (ci, hi, h, ch_label)
                for hi, h in enumerate(self._chapters[ci].get("hadiths", []))
            ]

        hits = [(ci, hi, h, lbl) for ci, hi, h, lbl in pool if hadith_has_match(h, text)]
        self._search_panel.show_results(hits, text)
        self._viewer.set_query(text)
        self._stack.setCurrentIndex(1)

    def _clear_search(self):
        self._search_mode = False
        self._search_box.blockSignals(True)
        self._search_box.clear()
        self._search_box.blockSignals(False)
        self._viewer.set_query("")
        self._stack.setCurrentIndex(0)
        if self._chapters:
            hadiths = self._chapters[self._cur_ch].get("hadiths", [])
            self._viewer.load_hadiths(hadiths)

    def _jump_from_search(self, ci: int, hi: int):
        if ci < 0 or ci >= len(self._chapters):
            return
        self._cur_ch = ci
        self._ch_bar.select_silent(ci)
        q       = self._search_box.text().strip()
        hadiths = self._chapters[ci].get("hadiths", [])
        self._viewer.load_hadiths(hadiths, q)
        self._viewer.jump_to_index(hi)
        self._stack.setCurrentIndex(0)
        self._search_mode = False


# ─────────────────────────────────────────────────────────────────────────────
#  Main BooksTab
# ─────────────────────────────────────────────────────────────────────────────

class BooksTab(QWidget):

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._index: dict = {}   # tree-item uid → {paths, meta}
        self._build()
        QTimer.singleShot(0, self._load_tree)

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        spl = QSplitter(Qt.Orientation.Horizontal)
        spl.setHandleWidth(5)
        spl.setChildrenCollapsible(False)

        # ── Sidebar ───────────────────────────────────────────────────────
        sb  = QFrame()
        sb.setObjectName("sidePanel")
        sb.setMinimumWidth(185)
        sb.setMaximumWidth(310)
        sbl = QVBoxLayout(sb)
        sbl.setContentsMargins(0, 0, 0, 0)
        sbl.setSpacing(0)

        hd = QLabel("📚  المكتبة")
        hd.setObjectName("panelHeader")
        hd.setFixedHeight(36)
        hd.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sbl.addWidget(hd)

        rf = QPushButton("🔄  تحديث")
        rf.setObjectName("actionButton")
        rf.setFixedHeight(26)
        rf.clicked.connect(self._load_tree)
        sbl.addWidget(rf)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._tree.setObjectName("chainList")
        self._tree.setStyleSheet("""
            QTreeWidget {
                font-family: 'Amiri', 'Traditional Arabic', Arial;
                font-size: 13px;
            }
            QTreeWidget::item { padding: 5px 8px; }
        """)
        self._tree.itemClicked.connect(self._on_click)
        sbl.addWidget(self._tree, 1)

        spl.addWidget(sb)

        # ── Reader ────────────────────────────────────────────────────────
        self._reader = BookReaderPane()
        spl.addWidget(self._reader)

        spl.setSizes([240, 960])
        root.addWidget(spl)

    # ── Tree ──────────────────────────────────────────────────────────────

    def _load_tree(self):
        self._tree.clear()
        self._index.clear()
        books = find_books()

        if not books:
            QTreeWidgetItem(self._tree, ["لا توجد كتب في  Data/BOOKS"])
            return

        for cat, book_map in books.items():
            cat_item = QTreeWidgetItem(self._tree, [f"📁  {cat}"])
            cat_item.setExpanded(True)
            f = QFont(cat_item.font(0))
            f.setBold(True)
            cat_item.setFont(0, f)

            for bname, info in book_map.items():
                # Read first chapter file for title/author
                meta  = {}
                title = bname
                first = load_json(info["chapters"][0]) if info["chapters"] else None
                if first:
                    meta = first.get("metadata", {})
                    ar   = meta.get("arabic",  {})
                    en   = meta.get("english", {})
                    title = ar.get("title") or en.get("title") or bname

                n_ch  = len(info["chapters"])
                child = QTreeWidgetItem(cat_item, [f"📖  {title}  ({n_ch} باب)"])

                author = (meta.get("arabic", {}).get("author") or
                          meta.get("english", {}).get("author") or "")
                child.setToolTip(0, author)

                uid = id(child)
                self._index[uid] = {"paths": info["chapters"], "meta": meta}
                child.setData(0, Qt.ItemDataRole.UserRole, uid)

    def _on_click(self, item: QTreeWidgetItem, _col: int):
        uid = item.data(0, Qt.ItemDataRole.UserRole)
        if not uid or uid not in self._index:
            return
        d = self._index[uid]
        self._reader.start_load(d["paths"], d["meta"])
        if hasattr(self.main_window, "status_label"):
            self.main_window.status_label.setText("📖  جارٍ تحميل الكتاب...")