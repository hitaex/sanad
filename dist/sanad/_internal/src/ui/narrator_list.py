"""
Narrator list widget with custom delegate.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

NarratorSubtitleRole = Qt.ItemDataRole.UserRole + 1


class NarratorListDelegate(QStyledItemDelegate):
    """Paint narrator name with كنية، نسب، لقب in smaller grey italic below."""

    def paint(self, painter, option, index):
        painter.save()
        name = index.data(Qt.ItemDataRole.DisplayRole) or ""
        subtitle = index.data(NarratorSubtitleRole) or ""

        # Background
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

        name_rect = option.rect.adjusted(4, 2, -4, -2)
        if subtitle:
            name_rect.setHeight(option.rect.height() // 2)

        painter.setPen(option.palette.color(QPalette.ColorGroup.Normal, QPalette.ColorRole.Text))
        painter.setFont(option.font)
        painter.drawText(name_rect, Qt.AlignmentFlag.AlignRight | Qt.TextFlag.TextWordWrap, name)

        if subtitle:
            sub_rect = option.rect.adjusted(4, option.rect.height() // 2, -4, -2)
            font = option.font
            font.setPointSize(max(8, font.pointSize() - 2))
            font.setItalic(True)
            painter.setFont(font)
            painter.setPen(QColor(100, 100, 100))
            painter.drawText(sub_rect, Qt.AlignmentFlag.AlignRight | Qt.TextFlag.TextWordWrap, subtitle)

        painter.restore()

    def sizeHint(self, option, index):
        subtitle = index.data(NarratorSubtitleRole) or ""
        h = option.fontMetrics.height() + 4
        if subtitle:
            h += option.fontMetrics.height() + 2
        return QSize(option.rect.width(), h)


class NarratorListView(QListWidget):
    """List widget for displaying narrators with custom delegate."""
    narratorDoubleClicked = pyqtSignal(object)  # Emits narrator data

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegate(NarratorListDelegate(self))
        self.itemDoubleClicked.connect(self._on_item_double_clicked)

    def add_narrator(self, narrator):
        """Add narrator to list."""
        item = QListWidgetItem(narrator.name)
        item.setData(Qt.ItemDataRole.UserRole, narrator)

        # Subtitle: كنية، نسب، لقب
        bi = narrator.basic_info
        parts = [bi.get('الكنية', ''), bi.get('النسب', ''), bi.get('اللقب', '')]
        subtitle = ' · '.join(p for p in parts if p)
        item.setData(NarratorSubtitleRole, subtitle)

        self.addItem(item)

    def _on_item_double_clicked(self, item):
        """Handle double click on narrator item."""
        narrator = item.data(Qt.ItemDataRole.UserRole)
        if narrator:
            self.narratorDoubleClicked.emit(narrator)

    def filter_items(self, text):
        """Filter items based on search text."""
        search_text = text.strip().lower()

        for i in range(self.count()):
            item = self.item(i)
            name_match = search_text in item.text().lower()
            subtitle = (item.data(NarratorSubtitleRole) or "").lower()
            subtitle_match = search_text in subtitle
            item.setHidden(not (name_match or subtitle_match))