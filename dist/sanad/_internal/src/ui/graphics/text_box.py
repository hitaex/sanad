"""
Editable text box graphics item.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class TextBox(QGraphicsRectItem):
    """Editable text box for canvas with production-ready resize."""

    MIN_W = 120
    MIN_H = 40
    MAX_W = 2000
    MAX_H = 2000
    PADDING = 12
    TEXT_WIDTH = 380

    def __init__(self, x, y, width=200, height=60, text="", app_ref=None):
        font = QFont("Amiri", 12)
        fm = QFontMetrics(font)
        text_height = fm.height()
        text_width = fm.horizontalAdvance(text) if text else 0

        w = max(min(text_width + self.PADDING * 2, self.MAX_W), self.MIN_W)
        h = max(min(text_height + self.PADDING * 2, self.MAX_H), self.MIN_H)

        super().__init__(0, 0, w, h)

        self.app_ref = app_ref
        self.setPos(x, y)

        self.setBrush(QBrush(QColor(255, 255, 255)))
        self.setPen(QPen(QColor(120, 120, 120), 2))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)

        self.text_item = QGraphicsTextItem(text, self)
        self.text_item.setDefaultTextColor(QColor(0, 0, 0))
        self.text_item.setFont(font)
        self.text_item.setTextWidth(self.TEXT_WIDTH)
        self.text_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.text_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        self.text_item.document().contentsChanged.connect(self.on_text_changed)

        self._update_rect_and_center()

    def _update_rect_and_center(self):
        """Resize within min/max when text changes."""
        # Set text width to None to allow it to expand horizontally as much as needed
        # Or set it to a very large value if we want wrapping at some extreme
        self.text_item.setTextWidth(-1) 
        
        text_rect = self.text_item.boundingRect()
        new_w = max(self.MIN_W, min(text_rect.width() + self.PADDING * 2, self.MAX_W))
        new_h = max(self.MIN_H, min(text_rect.height() + self.PADDING * 2, self.MAX_H))
        self.setRect(0, 0, new_w, new_h)
        self.text_item.setPos(
            (new_w - text_rect.width()) / 2,
            (new_h - text_rect.height()) / 2
        )

    def on_text_changed(self):
        """Handle text changes."""
        self._update_rect_and_center()
        # Save text to the narrator object if it exists
        if hasattr(self, 'narrator_data') and self.narrator_data:
            self.narrator_data.name = self.text_item.toPlainText()
        if self.app_ref and hasattr(self.app_ref, 'on_text_box_changed'):
            self.app_ref.on_text_box_changed(self)

    def contextMenuEvent(self, event):
        """Context menu for text box."""
        menu = QMenu()

        color_action = menu.addAction("🎨 تغيير اللون")
        delete_action = menu.addAction("🗑️ حذف")

        action = menu.exec(event.screenPos())

        if action == color_action:
            color = QColorDialog.getColor(self.brush().color(), None, "اختر لون الصندوق")
            if color.isValid():
                self.setBrush(QBrush(color))
        elif action == delete_action:
            if self.app_ref and hasattr(self.app_ref, 'remove_text_box'):
                self.app_ref.remove_text_box(self)