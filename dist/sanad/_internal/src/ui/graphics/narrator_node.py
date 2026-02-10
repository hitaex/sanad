"""
Narrator node graphics item.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from config import NARRATION_METHODS


class NarratorNode(QGraphicsRectItem):
    """Rectangular narrator node with hover, click, and text editing."""

    def __init__(self, narrator_name, narrator_id, level, total_levels, x, y,
                 method='default', width=200, height=100, is_branch=False,
                 app_ref=None, narrator_data=None):

        # Constants
        min_node_width = 150
        min_node_height = 60
        max_node_width = 400
        max_node_height = 300
        text_padding = 25

        # Calculate text size
        font = QFont("Amiri", 12, QFont.Weight.Bold)
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(narrator_name)
        text_height = fm.height()

        # Calculate box size
        width = max(min(text_width + text_padding * 2, max_node_width), min_node_width)
        height = max(min(text_height + text_padding * 2, max_node_height), min_node_height)

        super().__init__(0, 0, width, height)

        self.narrator_name = narrator_name
        self.narrator_id = narrator_id
        self.level = level
        self.total_levels = total_levels
        self.method = method
        self.width = width
        self.height = height
        self.is_branch = is_branch
        self.app_ref = app_ref
        self.narrator_data = narrator_data

        self.setPos(x, y)

        # Colors
        is_blank = False
        if narrator_data:
            if isinstance(narrator_data, dict):
                is_blank = narrator_data.get('blank', False)
            else:
                is_blank = getattr(narrator_data, 'blank', False)

        if is_blank:
            self.color = QColor(255, 255, 220)  # Light yellow for editing
            self.border_color = QColor(200, 180, 100)
        elif is_branch:
            self.color = QColor(245, 245, 245)
            self.border_color = QColor(100, 100, 100)
        elif not level:
            self.color = QColor(255, 255, 255)
            self.border_color = QColor(80, 80, 80)
        elif level == total_levels - 1:
            self.color = QColor(240, 240, 240)
            self.border_color = QColor(100, 100, 100)
        else:
            self.color = QColor(250, 250, 250)
            self.border_color = QColor(120, 120, 120)

        self.setBrush(QBrush(self.color))
        self.setPen(QPen(self.border_color, 2))

        # Make interactive
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        # Text item
        self.text_item = QGraphicsTextItem(narrator_name, self)
        self.text_item.setDefaultTextColor(QColor(0, 0, 0))
        self.text_item.setFont(font)
        
        is_blank = False
        if narrator_data:
            if isinstance(narrator_data, dict):
                is_blank = narrator_data.get('blank', False)
            else:
                is_blank = getattr(narrator_data, 'blank', False)
                
        self.text_item.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextEditorInteraction
            if is_blank
            else Qt.TextInteractionFlag.NoTextInteraction
        )
        self.text_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        # Connect text changes for editable boxes
        if is_blank:
            self.text_item.document().contentsChanged.connect(self.update_node_size)

        # Center text
        text_rect = self.text_item.boundingRect()
        text_x = (width - text_rect.width()) / 2
        text_y = (height - text_rect.height()) / 2
        self.text_item.setPos(text_x, text_y)

        # Connections and hover
        self.connections = []
        self.hover_bubble = None

        # Tooltip
        tooltip_text = f"{narrator_name}\nانقر مرتين للتفاصيل"
        if is_branch:
            tooltip_text = f"(ح) تحويل السند\n{narrator_name}"
        self.setToolTip(tooltip_text)

    def update_node_size(self):
        """Update node size when text changes."""
        text = self.text_item.toPlainText()

        # Update narrator data
        if self.narrator_data:
            if isinstance(self.narrator_data, dict):
                self.narrator_data['name'] = text
            else:
                self.narrator_data.name = text
            self.narrator_name = text

        # Recalculate size
        font = QFont("Amiri", 12, QFont.Weight.Bold)
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(text)
        text_height = fm.height()

        min_node_width = 150
        min_node_height = 60
        max_node_width = 400
        max_node_height = 300
        text_padding = 25

        new_width = max(min(text_width + text_padding * 2, max_node_width), min_node_width)
        new_height = max(min(text_height + text_padding * 2, max_node_height), min_node_height)

        self.setRect(0, 0, new_width, new_height)
        self.width = new_width
        self.height = new_height

        # Re-center text
        text_rect = self.text_item.boundingRect()
        text_x = (new_width - text_rect.width()) / 2
        text_y = (new_height - text_rect.height()) / 2
        self.text_item.setPos(text_x, text_y)

        # Update name and notify app
        if self.app_ref and hasattr(self.app_ref, 'on_node_text_changed'):
            self.app_ref.on_node_text_changed(self.narrator_id, text)

        # Update connections
        self.on_narrator_text_changed()

    def on_narrator_text_changed(self):
        """Update connections when node geometry or text changes."""
        # Update name if text changed (for editable nodes)
        if self.text_item:
            new_name = self.text_item.toPlainText()
            if new_name != self.narrator_name:
                self.narrator_name = new_name
                if self.narrator_data:
                    if isinstance(self.narrator_data, dict):
                        self.narrator_data['name'] = new_name
                    else:
                        self.narrator_data.name = new_name
                if self.app_ref and hasattr(self.app_ref, 'on_node_text_changed'):
                    self.app_ref.on_node_text_changed(self.narrator_id, new_name)

        for line in self.connections:
            try:
                if line and hasattr(line, 'updatePosition'):
                    line.updatePosition()
            except Exception:
                pass

    def add_connection(self, line):
        """Add a connection line."""
        self.connections.append(line)

    def itemChange(self, change, value):
        """Handle item changes (position, selection)."""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            for line in list(self.connections):
                try:
                    if line and hasattr(line, 'updatePosition'):
                        line.updatePosition()
                except Exception as e:
                    if line in self.connections:
                        self.connections.remove(line)
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            # Highlight with a distinct color when selected
            is_selected = bool(value)
            if is_selected:
                self.setPen(QPen(QColor(0, 120, 215), 3)) # Blue highlight
            else:
                self.setPen(QPen(self.border_color, 2))
                
        return super().itemChange(change, value)

    def hoverEnterEvent(self, event):
        """Highlight on hover and show Ibn Hajar comment."""
        self.setPen(QPen(QColor(60, 60, 60), 3))

        if self.narrator_data and self.app_ref:
            basic_info = self.narrator_data.get('basic_info', {})
            ibn_hajar_rank = basic_info.get('الرتبة عند ابن حجر', '')

            if ibn_hajar_rank:
                bubble_text = f"قول ابن حجر: {ibn_hajar_rank}"
                label = QLabel(bubble_text)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet(
                    "background-color: rgb(255, 255, 220); border: 1px solid rgb(180, 180, 180); "
                    "border-radius: 4px; padding: 10px 14px; font-family: Amiri; font-size: 12px; color: black;"
                )
                label.setFont(QFont("Amiri", 12))
                label.setWordWrap(True)
                label.adjustSize()
                box_w = label.size().width() + 4
                box_h = label.size().height() + 4
                label.setFixedSize(box_w, box_h)
                bubble_x = (self.width - box_w) / 2
                bubble_y = -box_h - 12
                proxy = QGraphicsProxyWidget(self)
                proxy.setWidget(label)
                proxy.setPos(bubble_x, bubble_y)
                proxy.setZValue(1000)
                self.hover_bubble = proxy

        if self.app_ref:
            self.app_ref.on_graph_node_hovered(self.narrator_name)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Remove highlight and bubble."""
        self.setPen(QPen(self.border_color, 2))
        if self.hover_bubble:
            try:
                sc = self.hover_bubble.scene()
                if sc:
                    sc.removeItem(self.hover_bubble)
            except Exception:
                pass
            self.hover_bubble = None

        if self.app_ref:
            self.app_ref.on_graph_node_hover_ended(self.narrator_name)
        super().hoverLeaveEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Handle double-click to show narrator details."""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.app_ref:
                self.app_ref.on_graph_node_double_clicked(self.narrator_id)
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        """Context menu for node operations."""
        menu = QMenu()

        add_child_action = menu.addAction("➕ إضافة راوٍ تابع (ابن)")
        delete_action = menu.addAction("🗑️ حذف")
        
        color_action = menu.addAction("🎨 تغيير لون الصندوق")

        action = menu.exec(event.screenPos())

        if action == add_child_action:
            if self.app_ref:
                self.app_ref.add_narrator_after_node(self.narrator_id, self)
        elif action == delete_action:
            if self.app_ref and hasattr(self.app_ref, 'remove_narrator_by_id'):
                self.app_ref.remove_narrator_by_id(self.narrator_id)
        elif action == color_action:
            color = QColorDialog.getColor(self.brush().color(), None, "اختر لون الصندوق")
            if color.isValid():
                self.color = color
                self.setBrush(QBrush(color))