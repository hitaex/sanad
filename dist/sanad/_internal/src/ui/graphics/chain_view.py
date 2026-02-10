"""
Custom graphics view for chain visualization.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from ui.graphics.text_box import TextBox
from ui.graphics.narrator_node import NarratorNode
from ui.graphics.connection_line import ConnectionLine
import config


class ChainGraphicsView(QGraphicsView):
    """Custom graphics view for chain visualization."""

    node_clicked = pyqtSignal(int)  # narrator_id

    def __init__(self, app_ref=None):
        super().__init__()

        self.app_ref = app_ref
        self.zoom_level = 1.0

        # For rubber band selection
        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self.origin = QPoint()

        # Setup rendering
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # White background
        self.setBackgroundBrush(QBrush(QColor(255, 255, 255)))

        # Create scene
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-3000, -3000, 6000, 6000)
        self.setScene(self.scene)

        # Connect scene mouse events
        self.scene.mousePressEvent = self.sceneMousePressEvent
        self.scene.mouseDoubleClickEvent = self.sceneMouseDoubleClickEvent

    def mousePressEvent(self, event):
        """Handle mouse press for right-click selection."""
        if event.button() == Qt.MouseButton.RightButton:
            self.origin = event.pos()
            # Do not show rubber band yet, wait for move to distinguish from single click
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for rubber band selection."""
        if (event.buttons() & Qt.MouseButton.RightButton) and not self.origin.isNull():
            # If the mouse moved enough from the origin, start showing the rubber band
            if (event.pos() - self.origin).manhattanLength() > QApplication.startDragDistance():
                if not self.rubber_band.isVisible():
                    self.rubber_band.show()
                    # Deselect all if not holding Shift/Ctrl
                    if not (event.modifiers() & (Qt.KeyboardModifier.ShiftModifier | Qt.KeyboardModifier.ControlModifier)):
                        self.scene.clearSelection()
                
                self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release to select items."""
        if self.rubber_band.isVisible():
            self.rubber_band.hide()
            selection_rect = self.rubber_band.geometry()
            scene_rect = self.mapToScene(selection_rect).boundingRect()
            
            # Create a path for selection
            path = QPainterPath()
            path.addRect(scene_rect)
            self.scene.setSelectionArea(path)
            
            # Reset origin to prevent accidental rubber band on next move without press
            self.origin = QPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            # If it was a single right click without drag, origin was set but rubber band never shown.
            # We should probably reset origin and let context menu event trigger naturally.
            self.origin = QPoint()
            super().mouseReleaseEvent(event)
        else:
            super().mouseReleaseEvent(event)

    def sceneMousePressEvent(self, event):
        """Handle mouse press on scene."""
        # Only handle left click deselect here, right click is handled in mousePressEvent
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.scene.itemAt(event.scenePos(), QTransform())
            if item is None or (isinstance(item, QGraphicsTextItem) and
                                (item.parentItem() is None or not isinstance(item.parentItem(), NarratorNode))):
                for selected_item in self.scene.selectedItems():
                    selected_item.setSelected(False)
                if self.app_ref:
                    self.app_ref.on_canvas_clicked()
        QGraphicsScene.mousePressEvent(self.scene, event)

    def sceneMouseDoubleClickEvent(self, event):
        """Handle double-click."""
        item = self.scene.itemAt(event.scenePos(), QTransform())
        if isinstance(item, NarratorNode):
            self.node_clicked.emit(item.narrator_id)
        elif isinstance(item, QGraphicsTextItem) and isinstance(item.parentItem(), NarratorNode):
            self.node_clicked.emit(item.parentItem().narrator_id)
        else:
            QGraphicsScene.mouseDoubleClickEvent(self.scene, event)

    def add_text_box_at_center(self):
        """Add text box at center of visible area."""
        if not hasattr(self, 'scene'):
            return

        visible_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        center_x = visible_rect.center().x()
        center_y = visible_rect.center().y()

        text_box = TextBox(center_x - 100, center_y - 30, 200, 60, "", self.app_ref)
        self.scene.addItem(text_box)
        text_box.setSelected(True)

    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        factor = 1.15
        if event.angleDelta().y() > 0:
            if self.zoom_level < 5.0:
                self.zoom_level *= factor
                self.scale(factor, factor)
        else:
            if self.zoom_level > 0.2:
                self.zoom_level /= factor
                self.scale(1 / factor, 1 / factor)

    def clear_scene(self):
        """Clear all items from scene optimized."""
        # Using a set to quickly check for items we want to keep might be an option,
        # but here we just want to clear everything efficiently.
        # scene.clear() is already quite optimized in Qt, but we have custom logic for connections.
        
        # Reset connections in nodes to avoid dangling references
        for item in self.scene.items():
            if isinstance(item, NarratorNode):
                item.connections = []
                
        self.scene.clear()