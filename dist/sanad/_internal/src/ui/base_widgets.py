"""
Base widgets reused across the application.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


class ClickableLabel(QLabel):
    """Label that emits clicked signal."""
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class ResizableSplitter(QSplitter):
    """Custom splitter with stretch factors and optional resizing limits."""

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setChildrenCollapsible(False)
        self.setHandleWidth(8)
        self.splitterMoved.connect(self._handle_move)

    def _handle_move(self, pos, index):
        """Enforce resizing limits if needed."""
        # This is a generic handler, specific limits can be added per usage 
        # or we can set default min/max sizes on widgets.
        pass

    def addWidgetWithStretch(self, widget, stretch, min_width=None, max_width=None):
        """Add widget with stretch factor and optional limits."""
        if min_width:
            widget.setMinimumWidth(min_width)
        if max_width:
            widget.setMaximumWidth(max_width)
        super().addWidget(widget)
        self.setStretchFactor(self.count() - 1, stretch)


class StyledPushButton(QPushButton):
    """Styled push button with custom properties."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)