"""
Connection line graphics item.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import math
from config import NARRATION_METHODS, debug_print


class ConnectionLine(QGraphicsLineItem):
    """Connection line with green-to-red color coding."""

    def __init__(self, start_node, end_node=None, method='default', curved=False):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.method = method
        self.curved = curved

        # Get color and thickness from method
        method_info = NARRATION_METHODS.get(method, NARRATION_METHODS['default'])
        color = method_info['color']
        thickness = method_info['thickness']

        # Set pen
        pen = QPen(color, thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.setPen(pen)

        # Add arrow
        self.arrow = QGraphicsPolygonItem(self)
        self.arrow.setBrush(QBrush(color))
        self.arrow.setPen(QPen(color))

        # Add to nodes
        try:
            if start_node:
                start_node.add_connection(self)
            if end_node:
                end_node.add_connection(self)
        except Exception as e:
            debug_print(f"ConnectionLine.__init__: Error - {e}")

        # Tooltip
        self.setToolTip(f"طريقة الرواية: {method_info['label']}")

        self._label_group = None
        self._label_size = (0, 0)

        self.updatePosition()

    def set_method_label(self, group, box_w, box_h):
        """Attach method label so it sticks to line center."""
        self._label_group = group
        self._label_size = (box_w, box_h)

    def updatePosition(self):
        """Update line and arrow position."""
        try:
            if not self.start_node or not self.start_node.scene():
                debug_print("ConnectionLine: start_node not in scene")
                return

            start_rect = self.start_node.sceneBoundingRect()
            start_x = start_rect.center().x()
            start_y = start_rect.bottom()

            if self.end_node:
                if not self.end_node.scene():
                    debug_print("ConnectionLine: end_node not in scene")
                    return
                end_rect = self.end_node.sceneBoundingRect()
                end_x = end_rect.center().x()
                end_y = end_rect.top()
            else:
                end_x = start_x
                end_y = start_y + 140
        except RuntimeError as e:
            debug_print(f"ConnectionLine.updatePosition: RuntimeError - {e}")
            return
        except Exception as e:
            debug_print(f"ConnectionLine.updatePosition: Error - {e}")
            return

        if self.curved:
            # Create curved path
            path = QPainterPath()
            path.moveTo(start_x, start_y)

            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2

            curve_offset = 30
            ctrl1_x = mid_x + curve_offset
            ctrl1_y = start_y + (end_y - start_y) * 0.3
            ctrl2_x = mid_x + curve_offset
            ctrl2_y = start_y + (end_y - start_y) * 0.7

            path.cubicTo(ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y, end_x, end_y)

            if not hasattr(self, 'path_item') or (self.path_item.scene() != self.start_node.scene()
                                                  and self.start_node.scene()):
                self.path_item = QGraphicsPathItem()
                method_info = NARRATION_METHODS.get(self.method, NARRATION_METHODS['default'])
                color = method_info['color']
                thickness = method_info['thickness']
                pen = QPen(color, thickness)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                self.path_item.setPen(pen)
                self.path_item.setZValue(-1)
                if self.start_node.scene():
                    self.start_node.scene().addItem(self.path_item)

            if hasattr(self, 'path_item'):
                self.path_item.setPath(path)

            self.setLine(0, 0, 0, 0)
            self.updateArrow(end_x, end_y, ctrl2_x, ctrl2_y)
        else:
            if hasattr(self, 'path_item') and self.path_item.scene():
                self.path_item.scene().removeItem(self.path_item)
                delattr(self, 'path_item')
            self.setLine(start_x, start_y, end_x, end_y)
            self.updateArrow(end_x, end_y, start_x, start_y)

        # Stick method label to center
        if getattr(self, '_label_group', None) and self._label_group.scene():
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            bw, bh = self._label_size
            self._label_group.setPos(mid_x - bw / 2, mid_y - bh / 2)

    def updateArrow(self, x, y, from_x, from_y):
        """Draw arrow at the end of the line."""
        angle = math.atan2(y - from_y, x - from_x)
        arrow_size = 10

        p1 = QPointF(x, y)
        p2 = QPointF(
            x - arrow_size * math.cos(angle - math.pi / 6),
            y - arrow_size * math.sin(angle - math.pi / 6)
        )
        p3 = QPointF(
            x - arrow_size * math.cos(angle + math.pi / 6),
            y - arrow_size * math.sin(angle + math.pi / 6)
        )

        arrow_polygon = QPolygonF([p1, p2, p3])
        self.arrow.setPolygon(arrow_polygon)