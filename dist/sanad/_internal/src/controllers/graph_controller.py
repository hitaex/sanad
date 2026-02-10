# Standard imports
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# These will be resolved at runtime since src is in sys.path
from config import NARRATION_METHODS

def get_narrator_node_class():
    from ui.graphics.narrator_node import NarratorNode
    return NarratorNode

def get_connection_line_class():
    from ui.graphics.connection_line import ConnectionLine
    return ConnectionLine

class GraphController:
    """Handles positioning and drawing of nodes and connections."""

    def __init__(self):
        self.node_spacing_x = 250
        self.node_spacing_y = 150

    def draw_vertical_tree(self, scene, chain_items, narrators_dict, app_ref, show_labels=False):
        """Draw vertical tree layout with N-ary branching support."""
        if not chain_items:
            return

        NarratorNode = get_narrator_node_class()
        ConnectionLine = get_connection_line_class()

        # Track horizontal position to avoid overlap
        self.next_x_at_level = {}

        def draw_recursive(narrator, method, level, total_levels, parent_node=None):
            # Prepare narrator data
            if isinstance(narrator, dict):
                n_name = narrator.get('name', '')
                n_id = narrator.get('id', 0)
                n_dict = narrator
            else:
                n_name = narrator.name
                n_id = narrator.id
                n_dict = narrator.to_dict()
                if hasattr(narrator, 'blank'):
                    n_dict['blank'] = narrator.blank

            # Check for loaded visual data
            visual = getattr(narrator, '_visual_load', None)
            
            if visual:
                x = visual.get('x', 0)
                y = visual.get('y', 0)
            else:
                # Determine auto position for this level
                if level not in self.next_x_at_level:
                    self.next_x_at_level[level] = 0
                
                x = self.next_x_at_level[level]
                y = 50 + level * self.node_spacing_y
                self.next_x_at_level[level] += self.node_spacing_x

            # Create node
            node = NarratorNode(
                n_name, n_id, level, total_levels,
                x, y, method=method, app_ref=app_ref, narrator_data=n_dict
            )
            scene.addItem(node)

            # Apply loaded visual styles
            if visual:
                if 'width' in visual and 'height' in visual:
                    node.setRect(0, 0, visual['width'], visual['height'])
                if 'color' in visual:
                    node.setBrush(QBrush(QColor(visual['color'])))
                if 'border_color' in visual:
                    node.setPen(QPen(QColor(visual['border_color']), 2))
                if 'text_color' in visual:
                    node.text_item.setDefaultTextColor(QColor(visual['text_color']))
                
                # Font styles
                font = node.text_item.font()
                if 'font_size' in visual:
                    font.setPointSize(visual['font_size'])
                if 'bold' in visual:
                    font.setBold(visual['bold'])
                if 'italic' in visual:
                    font.setItalic(visual['italic'])
                node.text_item.setFont(font)
                
                # Re-center text after possible size change
                text_rect = node.text_item.boundingRect()
                node.text_item.setPos(
                    (node.rect().width() - text_rect.width()) / 2,
                    (node.rect().height() - text_rect.height()) / 2
                )

            # Connect to parent
            if parent_node:
                line = ConnectionLine(parent_node, node, method=method, curved=(level > 0))
                scene.addItem(line)
                if show_labels and method != 'default':
                    app_ref.add_method_label(parent_node, node, method, line)

            # Draw children
            if hasattr(narrator, 'children') and narrator.children:
                for child, m in narrator.children:
                    draw_recursive(child, m, level + 1, total_levels, node)

        # Start drawing from root nodes
        for i, item in enumerate(chain_items):
            if isinstance(item, tuple) and item[0] != 'BRANCH':
                narrator, method = item
                draw_recursive(narrator, method, 0, len(chain_items))

    def draw_horizontal_tree(self, scene, chain_items, narrators_dict, app_ref, show_labels=False):
        """Draw horizontal tree layout with N-ary branching support."""
        if not chain_items:
            return

        NarratorNode = get_narrator_node_class()
        ConnectionLine = get_connection_line_class()

        self.next_y_at_level = {}

        def draw_recursive(narrator, method, level, total_levels, parent_node=None):
            if isinstance(narrator, dict):
                n_name = narrator.get('name', '')
                n_id = narrator.get('id', 0)
                n_dict = narrator
            else:
                n_name = narrator.name
                n_id = narrator.id
                n_dict = narrator.to_dict()
                if hasattr(narrator, 'blank'):
                    n_dict['blank'] = narrator.blank

            # Check for loaded visual data
            visual = getattr(narrator, '_visual_load', None)
            
            if visual:
                x = visual.get('x', 0)
                y = visual.get('y', 0)
            else:
                if level not in self.next_y_at_level:
                    self.next_y_at_level[level] = 0

                x = 50 + level * self.node_spacing_x
                y = self.next_y_at_level[level]
                self.next_y_at_level[level] += self.node_spacing_y

            node = NarratorNode(
                n_name, n_id, level, total_levels,
                x, y, method=method, app_ref=app_ref, narrator_data=n_dict
            )
            scene.addItem(node)

            # Apply loaded visual styles
            if visual:
                if 'width' in visual and 'height' in visual:
                    node.setRect(0, 0, visual['width'], visual['height'])
                if 'color' in visual:
                    node.setBrush(QBrush(QColor(visual['color'])))
                if 'border_color' in visual:
                    node.setPen(QPen(QColor(visual['border_color']), 2))
                if 'text_color' in visual:
                    node.text_item.setDefaultTextColor(QColor(visual['text_color']))
                
                # Font styles
                font = node.text_item.font()
                if 'font_size' in visual:
                    font.setPointSize(visual['font_size'])
                if 'bold' in visual:
                    font.setBold(visual['bold'])
                if 'italic' in visual:
                    font.setItalic(visual['italic'])
                node.text_item.setFont(font)
                
                # Re-center text after possible size change
                text_rect = node.text_item.boundingRect()
                node.text_item.setPos(
                    (node.rect().width() - text_rect.width()) / 2,
                    (node.rect().height() - text_rect.height()) / 2
                )

            if parent_node:
                line = ConnectionLine(parent_node, node, method=method, curved=(level > 0))
                scene.addItem(line)
                if show_labels and method != 'default':
                    app_ref.add_method_label(parent_node, node, method, line)

            if hasattr(narrator, 'children') and narrator.children:
                for child, m in narrator.children:
                    draw_recursive(child, m, level + 1, total_levels, node)

        for i, item in enumerate(chain_items):
            if isinstance(item, tuple) and item[0] != 'BRANCH':
                narrator, method = item
                draw_recursive(narrator, method, 0, len(chain_items))

    def draw_pyramid(self, scene, chain_items, narrators_dict, app_ref, show_labels=False):
        """Draw pyramid layout."""
        # For now, pyramid will use vertical logic as it's the most common for isnads
        self.draw_vertical_tree(scene, chain_items, narrators_dict, app_ref, show_labels)