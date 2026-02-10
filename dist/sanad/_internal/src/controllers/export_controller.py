"""
Export controller for saving and loading chains.
"""

import json
from datetime import datetime
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtPrintSupport import QPrinter


class ExportController:
    """Controller for export operations."""

    def export_image(self, chain_view, hadith_name, format='png'):
        """Export chain as image."""
        file_filter = "PNG Images (*.png)" if format == 'png' else "JPEG Images (*.jpg)"
        default_name = f"سند_{hadith_name if hadith_name else 'حديث'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"

        file_name, _ = QFileDialog.getSaveFileName(
            None,
            "حفظ صورة السند",
            default_name,
            file_filter
        )

        if file_name:
            try:
                rect = chain_view.scene.itemsBoundingRect()
                padding = 50

                pixmap = QPixmap(int(rect.width()) + 2 * padding, int(rect.height()) + 2 * padding)
                pixmap.fill(Qt.GlobalColor.white)

                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

                chain_view.scene.render(
                    painter,
                    QRectF(padding, padding, rect.width(), rect.height()),
                    rect
                )
                painter.end()

                pixmap.save(file_name, format.upper(), 95)
                return True

            except Exception as e:
                QMessageBox.critical(None, "خطأ", f"فشل حفظ الصورة: {str(e)}")
                return False
        return False

    def export_pdf(self, chain_view, hadith_name):
        """Export chain as PDF."""
        default_name = f"سند_{hadith_name if hadith_name else 'حديث'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        file_name, _ = QFileDialog.getSaveFileName(
            None,
            "حفظ PDF",
            default_name,
            "PDF Files (*.pdf)"
        )

        if file_name:
            try:
                printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
                printer.setOutputFileName(file_name)
                printer.setPageOrientation(QPageLayout.Orientation.Portrait)

                rect = chain_view.scene.itemsBoundingRect()

                painter = QPainter(printer)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

                chain_view.scene.render(painter, QRectF(), rect)
                painter.end()

                return True

            except Exception as e:
                QMessageBox.critical(None, "خطأ", f"فشل حفظ PDF: {str(e)}")
                return False
        return False

    def copy_to_clipboard(self, chain_view):
        """Copy canvas image to clipboard."""
        try:
            rect = chain_view.scene.itemsBoundingRect()
            if rect.isEmpty():
                QMessageBox.warning(None, "تحذير", "اللوحة فارغة")
                return False

            padding = 50

            # Create pixmap
            pixmap = QPixmap(int(rect.width()) + 2 * padding, int(rect.height()) + 2 * padding)
            pixmap.fill(Qt.GlobalColor.white)

            # Render scene to pixmap
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

            chain_view.scene.render(
                painter,
                QRectF(padding, padding, rect.width(), rect.height()),
                rect
            )
            painter.end()

            # Copy to clipboard
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(pixmap)

            return True

        except Exception as e:
            QMessageBox.critical(None, "خطأ", f"فشل نسخ الصورة: {str(e)}")
            return False

    def save_chain(self, chain_items, data, narrators_dict, scene=None):
        """Save current chain to file with visual attributes and .amn support."""
        default_name = f"سند_{data.get('hadith_name', 'حديث')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.amn"

        file_name, _ = QFileDialog.getSaveFileName(
            None,
            "حفظ السند",
            default_name,
            "AMN Files (*.amn);;JSON Files (*.json)"
        )

        if file_name:
            try:
                # Find all nodes and text boxes in the scene to get their visual attributes
                visual_data = {}
                if scene:
                    from ui.graphics.narrator_node import NarratorNode
                    from ui.graphics.text_box import TextBox
                    for item in scene.items():
                        if isinstance(item, NarratorNode):
                            visual_data[f"node_{item.narrator_id}"] = {
                                'x': item.pos().x(),
                                'y': item.pos().y(),
                                'width': item.rect().width(),
                                'height': item.rect().height(),
                                'color': item.brush().color().name(),
                                'border_color': item.pen().color().name(),
                                'text_color': item.text_item.defaultTextColor().name(),
                                'font_size': item.text_item.font().pointSize(),
                                'bold': item.text_item.font().bold(),
                                'italic': item.text_item.font().italic()
                            }
                
                def narrator_to_saveable(narrator, method):
                    n_id = narrator.id if hasattr(narrator, 'id') else narrator.get('id')
                    n_name = narrator.name if hasattr(narrator, 'name') else narrator.get('name')
                    
                    saveable = {
                        'type': 'NARRATOR',
                        'narrator_id': n_id,
                        'narrator_name': n_name,
                        'method': method
                    }
                    
                    # Add visual data if available
                    if f"node_{n_id}" in visual_data:
                        saveable['visual'] = visual_data[f"node_{n_id}"]
                    
                    # Store full details for EVERY narrator in .amn to ensure portability
                    # Since we are moving to DB, the recipient might not have the same DB
                    if isinstance(narrator, dict):
                        saveable['details'] = narrator
                    else:
                        saveable['details'] = narrator.to_dict()
                        # Manually include biographical data since to_dict might be limited
                        saveable['details']['basic_info'] = narrator.basic_info
                        saveable['details']['jarh_tadil'] = narrator.jarh_tadil
                        if getattr(narrator, 'blank', False):
                            saveable['details']['blank'] = True

                    if hasattr(narrator, 'children') and narrator.children:
                        saveable['children'] = [narrator_to_saveable(c, m) for c, m in narrator.children]
                    return saveable

                chain_data = []
                for item in chain_items:
                    if isinstance(item, tuple) and item[0] != 'BRANCH':
                        narrator, method = item
                        chain_data.append(narrator_to_saveable(narrator, method))

                data['chain'] = chain_data
                
                # Save independent text boxes
                if scene:
                    from ui.graphics.text_box import TextBox
                    text_boxes_data = []
                    for item in scene.items():
                        if isinstance(item, TextBox):
                            text_boxes_data.append({
                                'x': item.pos().x(),
                                'y': item.pos().y(),
                                'width': item.rect().width(),
                                'height': item.rect().height(),
                                'text': item.text_item.toPlainText(),
                                'color': item.brush().color().name(),
                                'border_color': item.pen().color().name(),
                                'text_color': item.text_item.defaultTextColor().name(),
                                'font_size': item.text_item.font().pointSize(),
                                'bold': item.text_item.font().bold(),
                                'italic': item.text_item.font().italic()
                            })
                    data['text_boxes'] = text_boxes_data

                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                return True

            except Exception as e:
                QMessageBox.critical(None, "خطأ", f"فشل حفظ السند: {str(e)}")
                return False
        return False

    def load_chain(self, narrators_dict):
        """Load chain from file with N-ary children support and .amn support."""
        file_name, _ = QFileDialog.getOpenFileName(
            None,
            "فتح سند",
            "",
            "AMN Files (*.amn);;JSON Files (*.json)"
        )

        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                def load_recursive(item_data):
                    narrator_id = item_data.get('narrator_id')
                    
                    # Check if details are provided in the file (common in .amn)
                    details = item_data.get('details')
                    if details:
                        from models.narrator import Narrator
                        narrator = Narrator.from_dict(details)
                        if details.get('blank'):
                            narrator.blank = True
                        # Update global dict so it's available for search/other nodes
                        narrators_dict[narrator.id] = narrator
                    else:
                        narrator = narrators_dict.get(narrator_id)
                    
                    if not narrator:
                        from models.narrator import Narrator
                        narrator = Narrator(id=narrator_id, name=item_data.get('narrator_name', ''))
                    
                    # Restore visual data if present
                    visual = item_data.get('visual')
                    if visual:
                        # We store visual data in the narrator object temporarily
                        # so the GraphController can use it during drawing
                        narrator._visual_load = visual

                    method = item_data.get('method', 'عن')
                    
                    if 'children' in item_data:
                        narrator.children = []
                        for child_data in item_data['children']:
                            child_narrator, child_method = load_recursive(child_data)
                            narrator.children.append((child_narrator, child_method))
                    
                    return narrator, method

                chain_items = []
                for item_data in data.get('chain', []):
                    if item_data.get('type') == 'NARRATOR':
                        narrator, method = load_recursive(item_data)
                        chain_items.append((narrator, method))

                return chain_items, data

            except Exception as e:
                QMessageBox.critical(None, "خطأ", f"فشل تحميل السند: {str(e)}")
                return [], {}
        return [], {}