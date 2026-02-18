"""
Graph tab UI component.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from datetime import datetime
import json
from ui.base_widgets import ResizableSplitter, StyledPushButton
from ui.narrator_list import NarratorListView
from ui.graphics.chain_view import ChainGraphicsView
from ui.graphics.narrator_node import NarratorNode
from ui.graphics.text_box import TextBox
from ui.graphics.connection_line import ConnectionLine
from controllers.graph_controller import GraphController
from controllers.export_controller import ExportController
from config import NARRATION_METHODS, TABAQAT_OPTIONS
import config

class GraphTab(QWidget):
    """Graph tab for chain visualization and construction."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.chain_items = []
        self.chain_nodes = []
        self.expanded_branches = set()
        self.active_branch_index = None
        self.active_sub_branch = 0
        self._last_branch_node = None
        self._draw_chain_timer = None
        self._last_blank_id = -10000
        self._last_custom_id = -1000
        self.pending_parent_id = None

        self.graph_controller = GraphController()
        self.export_controller = ExportController()

        self.undo_stack = QUndoStack(self)

        self.setup_ui()

    def setup_ui(self):
        """Setup graph tab UI."""
        # Shortcuts for Undo/Redo
        self.undo_shortcut = QShortcut(QKeySequence.StandardKey.Undo, self)
        self.undo_shortcut.activated.connect(self.undo_stack.undo)
        self.redo_shortcut = QShortcut(QKeySequence.StandardKey.Redo, self)
        self.redo_shortcut.activated.connect(self.undo_stack.redo)

        # Shortcuts for Copy/Paste/Cut/Delete
        self.copy_shortcut = QShortcut(QKeySequence.StandardKey.Copy, self)
        self.copy_shortcut.activated.connect(self.copy_to_clipboard)
        self.paste_shortcut = QShortcut(QKeySequence.StandardKey.Paste, self)
        self.paste_shortcut.activated.connect(self.paste_from_clipboard)
        self.cut_shortcut = QShortcut(QKeySequence.StandardKey.Cut, self)
        self.cut_shortcut.activated.connect(self.cut_to_clipboard)
        self.delete_shortcut = QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Delete), self)
        self.delete_shortcut.activated.connect(self.remove_narrator)

        # Select All (Ctrl+A)
        self.select_all_shortcut = QShortcut(QKeySequence.StandardKey.SelectAll, self)
        self.select_all_shortcut.activated.connect(self.select_all_items)

        # Also support plain Delete key
        self.plain_delete_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Delete), self)
        self.plain_delete_shortcut.activated.connect(self.remove_narrator)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create panels
        left_panel = self.create_graph_control_panel()
        center_panel = self.create_visualization_panel()
        right_panel = self.create_graph_right_panel()

        # Use splitter for resizable panels
        splitter = ResizableSplitter(Qt.Orientation.Horizontal)
        splitter.addWidgetWithStretch(left_panel, 2, min_width=300, max_width=500)
        splitter.addWidgetWithStretch(center_panel, 5)
        splitter.addWidgetWithStretch(right_panel, 2, min_width=300, max_width=500)
        layout.addWidget(splitter)

    def create_graph_control_panel(self):
        """Create left control panel for graphing."""
        panel = QFrame()
        panel.setObjectName("sidePanel")
        panel.setMinimumWidth(350)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # Panel header
        header = QLabel("بناء السند")
        header.setObjectName("panelHeader")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Hadith name
        name_label = QLabel("اسم الحديث:")
        layout.addWidget(name_label)

        self.hadith_name = QLineEdit()
        self.hadith_name.setPlaceholderText("مثال: حديث إنما الأعمال بالنيات")
        self.hadith_name.setObjectName("inputField")
        layout.addWidget(self.hadith_name)

        # Matn section
        matn_label = QLabel("المتن (اختياري):")
        layout.addWidget(matn_label)

        self.matn_input = QTextEdit()
        self.matn_input.setPlaceholderText("أدخل متن الحديث هنا...")
        self.matn_input.setObjectName("inputField")
        self.matn_input.setMaximumHeight(100)
        layout.addWidget(self.matn_input)

        # Chain building
        chain_label = QLabel("السلسلة:")
        layout.addWidget(chain_label)

        # Current chain list
        self.chain_list = QListWidget()
        self.chain_list.setObjectName("chainList")
        self.chain_list.itemClicked.connect(self.on_chain_item_clicked)
        layout.addWidget(self.chain_list)

        # Chain management buttons
        manage_layout = QGridLayout()
        manage_layout.setSpacing(4)

        self.move_up_btn = StyledPushButton("⬆️ أعلى")
        self.move_up_btn.setToolTip("تحريك لأعلى (Ctrl+Up)")
        self.move_up_btn.clicked.connect(self.move_narrator_up)
        manage_layout.addWidget(self.move_up_btn, 0, 0)

        self.move_down_btn = StyledPushButton("⬇️ أسفل")
        self.move_down_btn.setToolTip("تحريك لأسفل (Ctrl+Down)")
        self.move_down_btn.clicked.connect(self.move_narrator_down)
        manage_layout.addWidget(self.move_down_btn, 0, 1)

        self.edit_btn = StyledPushButton("✏️ تعديل")
        self.edit_btn.clicked.connect(self.edit_narrator)
        manage_layout.addWidget(self.edit_btn, 1, 0)

        self.remove_btn = StyledPushButton("🗑️ حذف")
        self.remove_btn.setToolTip("حذف المحدد (Delete)")
        self.remove_btn.clicked.connect(self.remove_narrator)
        manage_layout.addWidget(self.remove_btn, 1, 1)

        layout.addLayout(manage_layout)

        # Add blank box button
        add_blank_btn = StyledPushButton("📦 إضافة صندوق فارغ")
        add_blank_btn.setObjectName("actionButton")
        add_blank_btn.setToolTip("إضافة صندوق نص فارغ قابل للتحرير إلى السند")
        add_blank_btn.clicked.connect(self.add_blank_box_to_chain)
        layout.addWidget(add_blank_btn)

        # Add text box button
        add_text_btn = StyledPushButton("📝 إضافة صندوق نص")
        add_text_btn.setObjectName("actionButton")
        add_text_btn.setToolTip("انقر لإضافة صندوق نص في وسط اللوحة")
        add_text_btn.clicked.connect(self.add_text_box_to_canvas)
        layout.addWidget(add_text_btn)

        # Clear button
        clear_btn = StyledPushButton("🗑️ مسح الكل")
        clear_btn.setObjectName("actionButton")
        clear_btn.clicked.connect(self.clear_chain)
        layout.addWidget(clear_btn)

        # Layout options
        options_group = QGroupBox("خيارات العرض")
        options_layout = QVBoxLayout()

        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["شجري عمودي", "شجري أفقي", "هرمي"])
        self.layout_combo.currentIndexChanged.connect(self.on_layout_changed)
        options_layout.addWidget(QLabel("نمط التخطيط:"))
        options_layout.addWidget(self.layout_combo)

        self.show_method_labels = QCheckBox("إظهار تسميات طرق الرواية")
        self.show_method_labels.setChecked(True)
        options_layout.addWidget(self.show_method_labels)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Export section
        export_label = QLabel("تصدير:")
        layout.addWidget(export_label)

        export_layout = QHBoxLayout()

        self.export_png_btn = StyledPushButton("🖼️ PNG")
        self.export_png_btn.setToolTip("Ctrl+E")
        self.export_png_btn.clicked.connect(lambda: self.export_image('png'))
        export_layout.addWidget(self.export_png_btn)

        self.export_pdf_btn = StyledPushButton("📄 PDF")
        self.export_pdf_btn.setToolTip("Ctrl+P")
        self.export_pdf_btn.clicked.connect(self.export_pdf)  # FIXED: was self.export_png_btn
        export_layout.addWidget(self.export_pdf_btn)

        self.copy_clipboard_btn = StyledPushButton("📋 نسخ")
        self.copy_clipboard_btn.setToolTip("نسخ الصورة إلى الحافظة (Ctrl+C)")
        self.copy_clipboard_btn.clicked.connect(self.copy_canvas_to_clipboard)
        export_layout.addWidget(self.copy_clipboard_btn)

        layout.addLayout(export_layout)

        # Save/Load chain
        file_layout = QHBoxLayout()

        save_btn = StyledPushButton("💾 حفظ")
        save_btn.setToolTip("Ctrl+S")
        save_btn.clicked.connect(self.save_chain)
        file_layout.addWidget(save_btn)

        load_btn = StyledPushButton("📂 فتح")
        load_btn.setToolTip("Ctrl+O")
        load_btn.clicked.connect(self.load_chain)
        file_layout.addWidget(load_btn)

        layout.addLayout(file_layout)

        layout.addStretch()

        return panel

    def create_visualization_panel(self):
        """Create center visualization panel."""
        panel = QFrame()
        panel.setObjectName("centerPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = self.create_graph_toolbar()
        layout.addWidget(toolbar)

        # Graphics view
        self.chain_view = ChainGraphicsView(app_ref=self.main_window)
        self.chain_view.node_clicked.connect(self.main_window.on_graph_node_double_clicked)
        layout.addWidget(self.chain_view, 1)

        # Legend
        legend = self.create_legend()
        layout.addWidget(legend)

        return panel

    def create_graph_toolbar(self):
        """Create visualization toolbar with full text editing controls."""
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        toolbar.setFixedHeight(44)

        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(8, 4, 8, 4)
        toolbar_layout.setSpacing(4)

        # Zoom controls
        for icon, tip, fn in [("➕", "Ctrl++", self.zoom_in), ("➖", "Ctrl+-", self.zoom_out),
                               ("🔄", "Ctrl+0", self.zoom_reset), ("⛶", "احتواء", self.zoom_fit)]:
            btn = StyledPushButton(icon)
            btn.setObjectName("toolbarButton")
            btn.setToolTip(tip)
            btn.clicked.connect(fn)
            toolbar_layout.addWidget(btn)

        toolbar_layout.addWidget(QLabel("|"))

        # Font family
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(["Amiri", "Traditional Arabic", "Arial", "Times New Roman", "Courier New"])
        self.font_family_combo.setFixedWidth(130)
        self.font_family_combo.setToolTip("نوع الخط")
        self.font_family_combo.currentTextChanged.connect(self.change_font_family)
        toolbar_layout.addWidget(self.font_family_combo)

        # Font size
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems([str(s) for s in [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32, 36, 48]])
        self.font_size_combo.setCurrentText("12")
        self.font_size_combo.setFixedWidth(55)
        self.font_size_combo.currentTextChanged.connect(self.change_font_size)
        toolbar_layout.addWidget(self.font_size_combo)

        toolbar_layout.addWidget(QLabel("|"))

        # Bold
        self.bold_btn = StyledPushButton("B")
        self.bold_btn.setFixedWidth(28)
        self.bold_btn.setCheckable(True)
        self.bold_btn.setToolTip("غامق (Ctrl+B)")
        self.bold_btn.setStyleSheet("font-weight: bold;")
        self.bold_btn.clicked.connect(self.toggle_bold)
        toolbar_layout.addWidget(self.bold_btn)

        # Italic
        self.italic_btn = StyledPushButton("I")
        self.italic_btn.setFixedWidth(28)
        self.italic_btn.setCheckable(True)
        self.italic_btn.setToolTip("مائل (Ctrl+I)")
        self.italic_btn.setStyleSheet("font-style: italic;")
        self.italic_btn.clicked.connect(self.toggle_italic)
        toolbar_layout.addWidget(self.italic_btn)

        # Underline
        self.underline_btn = StyledPushButton("U")
        self.underline_btn.setFixedWidth(28)
        self.underline_btn.setCheckable(True)
        self.underline_btn.setToolTip("تسطير")
        self.underline_btn.setStyleSheet("text-decoration: underline;")
        self.underline_btn.clicked.connect(self.toggle_underline)
        toolbar_layout.addWidget(self.underline_btn)

        # Strikethrough
        self.strike_btn = StyledPushButton("S̶")
        self.strike_btn.setFixedWidth(28)
        self.strike_btn.setCheckable(True)
        self.strike_btn.setToolTip("يتوسطه خط")
        self.strike_btn.clicked.connect(self.toggle_strikethrough)
        toolbar_layout.addWidget(self.strike_btn)

        toolbar_layout.addWidget(QLabel("|"))

        # Text color
        self.text_color_btn = StyledPushButton("A🎨")
        self.text_color_btn.setFixedWidth(44)
        self.text_color_btn.setToolTip("لون النص")
        self.text_color_btn.clicked.connect(self.change_text_color)
        toolbar_layout.addWidget(self.text_color_btn)

        # Background color
        self.bg_color_btn = StyledPushButton("◻🎨")
        self.bg_color_btn.setFixedWidth(44)
        self.bg_color_btn.setToolTip("لون خلفية الصندوق")
        self.bg_color_btn.clicked.connect(self.change_node_bg_color)
        toolbar_layout.addWidget(self.bg_color_btn)

        toolbar_layout.addWidget(QLabel("|"))

        # Alignment buttons
        self.align_right_btn = StyledPushButton("≡→")
        self.align_right_btn.setFixedWidth(32)
        self.align_right_btn.setToolTip("محاذاة لليمين")
        self.align_right_btn.clicked.connect(lambda: self.set_text_alignment(Qt.AlignmentFlag.AlignRight))
        toolbar_layout.addWidget(self.align_right_btn)

        self.align_center_btn = StyledPushButton("≡")
        self.align_center_btn.setFixedWidth(32)
        self.align_center_btn.setToolTip("توسيط")
        self.align_center_btn.clicked.connect(lambda: self.set_text_alignment(Qt.AlignmentFlag.AlignHCenter))
        toolbar_layout.addWidget(self.align_center_btn)

        self.align_left_btn = StyledPushButton("←≡")
        self.align_left_btn.setFixedWidth(32)
        self.align_left_btn.setToolTip("محاذاة لليسار")
        self.align_left_btn.clicked.connect(lambda: self.set_text_alignment(Qt.AlignmentFlag.AlignLeft))
        toolbar_layout.addWidget(self.align_left_btn)

        toolbar_layout.addStretch()
        return toolbar

    # ── Text editing helpers ──────────────────────────────────────────────────

    def get_selected_text_item(self):
        """Get the text item of the currently selected node or text box."""
        selected_items = self.chain_view.scene.selectedItems()
        if not selected_items:
            return None
        item = selected_items[0]
        if isinstance(item, (NarratorNode, TextBox)):
            return item.text_item
        elif isinstance(item, QGraphicsTextItem):
            return item
        return None

    def toggle_bold(self):
        text_item = self.get_selected_text_item()
        if text_item:
            cursor = text_item.textCursor()
            if not cursor.hasSelection():
                cursor.select(QTextCursor.SelectionType.Document)
            fmt = cursor.charFormat()
            weight = QFont.Weight.Bold if self.bold_btn.isChecked() else QFont.Weight.Normal
            fmt.setFontWeight(weight.value)
            cursor.mergeCharFormat(fmt)
            parent = text_item.parentItem()
            if parent and hasattr(parent, 'update_node_size'):
                parent.update_node_size()

    def toggle_italic(self):
        text_item = self.get_selected_text_item()
        if text_item:
            cursor = text_item.textCursor()
            if not cursor.hasSelection():
                cursor.select(QTextCursor.SelectionType.Document)
            fmt = cursor.charFormat()
            fmt.setFontItalic(self.italic_btn.isChecked())
            cursor.mergeCharFormat(fmt)
            parent = text_item.parentItem()
            if parent and hasattr(parent, 'update_node_size'):
                parent.update_node_size()

    def toggle_underline(self):
        text_item = self.get_selected_text_item()
        if text_item:
            cursor = text_item.textCursor()
            if not cursor.hasSelection():
                cursor.select(QTextCursor.SelectionType.Document)
            fmt = cursor.charFormat()
            fmt.setFontUnderline(self.underline_btn.isChecked())
            cursor.mergeCharFormat(fmt)

    def toggle_strikethrough(self):
        text_item = self.get_selected_text_item()
        if text_item:
            cursor = text_item.textCursor()
            if not cursor.hasSelection():
                cursor.select(QTextCursor.SelectionType.Document)
            fmt = cursor.charFormat()
            fmt.setFontStrikeOut(self.strike_btn.isChecked())
            cursor.mergeCharFormat(fmt)

    def change_font_size(self, size_str):
        text_item = self.get_selected_text_item()
        if text_item:
            try:
                size = int(size_str)
            except ValueError:
                return
            cursor = text_item.textCursor()
            if not cursor.hasSelection():
                cursor.select(QTextCursor.SelectionType.Document)
            fmt = cursor.charFormat()
            fmt.setFontPointSize(float(size))
            cursor.mergeCharFormat(fmt)
            parent = text_item.parentItem()
            if parent and hasattr(parent, 'update_node_size'):
                parent.update_node_size()

    def change_font_family(self, family):
        text_item = self.get_selected_text_item()
        if text_item:
            cursor = text_item.textCursor()
            if not cursor.hasSelection():
                cursor.select(QTextCursor.SelectionType.Document)
            fmt = cursor.charFormat()
            fmt.setFontFamilies([family])
            cursor.mergeCharFormat(fmt)
            parent = text_item.parentItem()
            if parent and hasattr(parent, 'update_node_size'):
                parent.update_node_size()

    def change_text_color(self):
        text_item = self.get_selected_text_item()
        if text_item:
            color = QColorDialog.getColor(Qt.GlobalColor.black, self, "اختر لون النص")
            if color.isValid():
                cursor = text_item.textCursor()
                if not cursor.hasSelection():
                    cursor.select(QTextCursor.SelectionType.Document)
                fmt = cursor.charFormat()
                fmt.setForeground(QBrush(color))
                cursor.mergeCharFormat(fmt)

    def change_node_bg_color(self):
        selected_items = self.chain_view.scene.selectedItems()
        if not selected_items:
            return
        item = selected_items[0]
        if isinstance(item, (NarratorNode, TextBox)):
            color = QColorDialog.getColor(item.brush().color(), self, "اختر لون الخلفية")
            if color.isValid():
                item.setBrush(QBrush(color))
                if isinstance(item, NarratorNode):
                    item.color = color

    def set_text_alignment(self, alignment):
        text_item = self.get_selected_text_item()
        if text_item:
            cursor = text_item.textCursor()
            block_fmt = cursor.blockFormat()
            block_fmt.setAlignment(alignment)
            cursor.mergeBlockFormat(block_fmt)
            text_item.setTextCursor(cursor)

    # ── Legend ────────────────────────────────────────────────────────────────

    def create_legend(self):
        """Create color legend for narration methods."""
        legend = QFrame()
        legend.setObjectName("legend")
        legend.setMaximumHeight(80)

        legend_layout = QVBoxLayout(legend)
        legend_layout.setContentsMargins(8, 4, 8, 4)

        title = QLabel("دليل طرق الرواية (أخضر = جيد، أحمر = ضعيف):")
        title.setObjectName("legendTitle")
        legend_layout.addWidget(title)

        colors_layout = QHBoxLayout()

        categories = [
            ("سماع صريح", 'حدثنا', 4),
            ("قراءة", 'قرأت عليه', 3),
            ("إجازة", 'أجاز لي', 2),
            ("محتمل", 'عن', 2),
            ("منقطع", 'بلغني', 1)
        ]

        for category, method, thickness in categories:
            item_layout = QHBoxLayout()

            line_label = QLabel()
            line_label.setFixedSize(30, 20)
            pixmap = QPixmap(30, 20)
            pixmap.fill(Qt.GlobalColor.white)
            painter = QPainter(pixmap)
            color = NARRATION_METHODS[method]['color']
            pen = QPen(color, thickness)
            painter.setPen(pen)
            painter.drawLine(0, 10, 30, 10)
            painter.end()
            line_label.setPixmap(pixmap)
            item_layout.addWidget(line_label)

            label = QLabel(category)
            label.setObjectName("legendLabel")
            item_layout.addWidget(label)

            colors_layout.addLayout(item_layout)

        colors_layout.addStretch()
        legend_layout.addLayout(colors_layout)

        return legend

    # ── Right panel ───────────────────────────────────────────────────────────

    def create_graph_right_panel(self):
        """Create right panel with narrator selection and details."""
        panel = QFrame()
        panel.setObjectName("sidePanel")
        panel.setFixedWidth(380)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.right_tabs = QTabWidget()
        self.right_tabs.setObjectName("rightTabs")

        selection_tab = self.create_narrator_selection_tab()
        self.right_tabs.addTab(selection_tab, "📚 اختيار راوٍ")

        details_tab = self.create_graph_details_tab()
        self.right_tabs.addTab(details_tab, "📖 التفاصيل")

        layout.addWidget(self.right_tabs)

        return panel

    def create_narrator_selection_tab(self):
        """Create narrator selection tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        instructions = QLabel("اختر راوياً ثم اضغط \"إضافة\" أو اضغط مرتين")
        instructions.setObjectName("instructionsLabel")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        search_label = QLabel("البحث:")
        layout.addWidget(search_label)

        self.narrator_search = QLineEdit()
        self.narrator_search.setPlaceholderText("اكتب اسم الراوي...")
        self.narrator_search.setObjectName("inputField")
        self.narrator_search.textChanged.connect(self.filter_narrator_list)
        layout.addWidget(self.narrator_search)

        self.narrator_list = NarratorListView()
        self.narrator_list.setObjectName("narratorList")
        self.narrator_list.narratorDoubleClicked.connect(self.on_narrator_double_click)
        layout.addWidget(self.narrator_list)

        method_label = QLabel("طريقة الرواية:")
        layout.addWidget(method_label)

        self.method_combo = QComboBox()
        self.method_combo.setObjectName("methodCombo")
        methods = list(NARRATION_METHODS.keys())
        methods.remove('default')
        self.method_combo.addItems(methods)
        self.method_combo.setCurrentText('عن')
        layout.addWidget(self.method_combo)

        buttons_layout = QHBoxLayout()

        add_btn = StyledPushButton("➕ إضافة راوٍ")
        add_btn.setObjectName("primaryButton")
        add_btn.setToolTip("Ctrl+N")
        add_btn.clicked.connect(self.add_selected_narrator)
        buttons_layout.addWidget(add_btn)

        custom_btn = StyledPushButton("✍️ إنشاء راوٍ جديد")
        custom_btn.setObjectName("actionButton")
        custom_btn.setToolTip("إنشاء راوٍ مخصص")
        custom_btn.clicked.connect(self.main_window.create_custom_narrator)
        buttons_layout.addWidget(custom_btn)

        layout.addLayout(buttons_layout)

        self.narrator_count_label = QLabel("عدد الرواة: 0")
        self.narrator_count_label.setObjectName("countLabel")
        layout.addWidget(self.narrator_count_label)

        return tab

    def create_graph_details_tab(self):
        """Create details tab for graphing."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        name_frame = QFrame()
        name_frame.setObjectName("detailsSection")
        name_layout = QVBoxLayout(name_frame)
        name_layout.setContentsMargins(8, 8, 8, 8)

        self.graph_selected_name = QLabel("لم يتم اختيار راوٍ")
        self.graph_selected_name.setObjectName("selectedName")
        self.graph_selected_name.setWordWrap(True)
        name_layout.addWidget(self.graph_selected_name)

        layout.addWidget(name_frame)

        info_frame = QFrame()
        info_frame.setObjectName("detailsSection")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(8, 8, 8, 8)

        info_title = QLabel("المعلومات الأساسية")
        info_title.setObjectName("sectionTitle")
        info_layout.addWidget(info_title)

        self.graph_basic_text = QTextBrowser()
        self.graph_basic_text.setObjectName("detailsText")
        info_layout.addWidget(self.graph_basic_text, 1)

        layout.addWidget(info_frame, 1)

        comments_frame = QFrame()
        comments_frame.setObjectName("detailsSection")
        comments_layout = QVBoxLayout(comments_frame)
        comments_layout.setContentsMargins(8, 8, 8, 8)

        comments_title = QLabel("الجرح والتعديل")
        comments_title.setObjectName("sectionTitle")
        comments_layout.addWidget(comments_title)

        self.graph_comments_text = QTextBrowser()
        self.graph_comments_text.setObjectName("detailsText")
        comments_layout.addWidget(self.graph_comments_text, 1)

        layout.addWidget(comments_frame, 2)

        return tab

    # ── Narrator list helpers ─────────────────────────────────────────────────

    def populate_narrator_list(self, narrators):
        """Populate the narrator list."""
        if not hasattr(self, 'narrator_list'):
            return

        self.narrator_list.clear()
        sorted_narrators = sorted(narrators, key=lambda x: x.name)
        for narrator in sorted_narrators:
            self.narrator_list.add_narrator(narrator)

        if hasattr(self, 'narrator_count_label'):
            self.narrator_count_label.setText(f"عدد الرواة: {len(narrators):,}")

    def filter_narrator_list(self, text):
        """Filter narrator list based on search text."""
        if hasattr(self, 'narrator_list'):
            self.narrator_list.filter_items(text)

    def on_narrator_double_click(self, narrator):
        """Handle double click on narrator."""
        self.add_selected_narrator()

    # ── Chain building ────────────────────────────────────────────────────────

    def add_selected_narrator(self):
        """Add selected narrator to chain or as child of pending parent."""
        if not hasattr(self, 'narrator_list'):
            return

        selected_nodes = [item for item in self.chain_view.scene.selectedItems() if isinstance(item, NarratorNode)]
        if len(selected_nodes) > 1:
            QMessageBox.warning(self, "تنبيه", "لا يمكن إضافة راوٍ عند اختيار أكثر من عقدة واحدة.")
            return

        current_item = self.narrator_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "معلومة", "الرجاء اختيار راوٍ أولاً")
            return

        import copy
        original_narrator = current_item.data(Qt.ItemDataRole.UserRole)
        narrator = copy.copy(original_narrator)

        if hasattr(narrator, 'children'):
            narrator.children = []

        method = self.method_combo.currentText()

        self.setUpdatesEnabled(False)
        try:
            if self.pending_parent_id is not None:
                if self._add_narrator_to_parent(self.pending_parent_id, narrator, method):
                    self.main_window.status_label.setText(
                        f"تمت إضافة: {narrator.name if hasattr(narrator, 'name') else narrator.get('name')} تابعاً")
                else:
                    self.main_window.status_label.setText("فشل إضافة التابع")
            else:
                self.chain_items.append((narrator, method))
                self.main_window.status_label.setText(
                    f"تمت إضافة: {narrator.name if hasattr(narrator, 'name') else narrator.get('name')}")

            self.update_chain_list()
            self.draw_chain()

            # Re-apply highlight if in pending mode
            if self.pending_parent_id is not None:
                for n in self.chain_nodes:
                    if n.narrator_id == self.pending_parent_id:
                        n.setPen(QPen(QColor(0, 120, 215), 4, Qt.PenStyle.DashLine))
                        n.setBrush(QBrush(n.color.darker(110)))
        finally:
            self.setUpdatesEnabled(True)

    def _add_narrator_to_parent(self, parent_id, child_narrator, method):
        """Internal helper to find parent and add child."""
        def find_recursive(narrators_list, target_id):
            for n, m in narrators_list:
                n_id = n.id if hasattr(n, 'id') else n.get('id')
                if n_id == target_id:
                    return n
                if hasattr(n, 'children') and n.children:
                    found = find_recursive(n.children, target_id)
                    if found:
                        return found
            return None

        parent = find_recursive(self.chain_items, parent_id)
        if parent:
            if not hasattr(parent, 'children'):
                parent.children = []
            parent.children.append((child_narrator, method))
            return True
        return False

    def _live_draw_chain(self):
        """Redraw graph after chain change."""
        if not hasattr(self, 'chain_view') or not self.chain_items:
            return
        self.draw_chain()

    def update_chain_list(self):
        """Update the chain list widget."""
        if not hasattr(self, 'chain_list'):
            return
        self.chain_list.clear()

        self.main_window.chain_items = self.chain_items
        visited = set()

        def add_narrator_to_list(narrator, method, depth=0):
            n_id = narrator.id if hasattr(narrator, 'id') else narrator.get('id')
            if n_id in visited:
                return
            visited.add(n_id)

            prefix = "  " * depth
            item_text = f"{prefix}{narrator.name if hasattr(narrator, 'name') else narrator.get('name')} ({method})"
            list_item = QListWidgetItem(item_text)
            list_item.setData(Qt.ItemDataRole.UserRole, ('NARRATOR', n_id))
            self.chain_list.addItem(list_item)

            if hasattr(narrator, 'children') and narrator.children:
                for child, m in narrator.children:
                    add_narrator_to_list(child, m, depth + 1)

        for item in self.chain_items:
            if isinstance(item, tuple) and item[0] != 'BRANCH':
                narrator, method = item
                add_narrator_to_list(narrator, method)

    def on_chain_item_clicked(self, item):
        """Handle click on chain list item."""
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return

        item_type, *args = data

        if item_type == 'NARRATOR':
            narrator_id = args[0]
            self.show_narrator_details(narrator_id)

            for node in self.chain_nodes:
                if node.narrator_id == narrator_id:
                    node.setSelected(True)
                    self.chain_view.centerOn(node)
                    break

    def select_all_items(self):
        """Select all items on the canvas."""
        if hasattr(self, 'chain_view') and self.chain_view.scene:
            for item in self.chain_view.scene.items():
                if item.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable:
                    item.setSelected(True)

    def move_narrator_up(self):
        """Move selected item up."""
        if not hasattr(self, 'chain_list'):
            return
        current_row = self.chain_list.currentRow()
        if current_row > 0 and current_row < len(self.chain_items):
            self.setUpdatesEnabled(False)
            try:
                self.chain_items[current_row], self.chain_items[current_row - 1] = \
                    self.chain_items[current_row - 1], self.chain_items[current_row]
                self.update_chain_list()
                self.draw_chain()
                self.chain_list.setCurrentRow(current_row - 1)
            finally:
                self.setUpdatesEnabled(True)

    def move_narrator_down(self):
        """Move selected item down."""
        if not hasattr(self, 'chain_list'):
            return
        current_row = self.chain_list.currentRow()
        if 0 <= current_row < len(self.chain_items) - 1:
            self.setUpdatesEnabled(False)
            try:
                self.chain_items[current_row], self.chain_items[current_row + 1] = \
                    self.chain_items[current_row + 1], self.chain_items[current_row]
                self.update_chain_list()
                self.draw_chain()
                self.chain_list.setCurrentRow(current_row + 1)
            finally:
                self.setUpdatesEnabled(True)

    def edit_narrator(self):
        """Edit selected narrator."""
        if not hasattr(self, 'chain_list'):
            return
        current_row = self.chain_list.currentRow()
        if current_row < 0 or current_row >= len(self.chain_items):
            return

        item = self.chain_items[current_row]
        if isinstance(item, tuple) and item[0] == 'BRANCH':
            QMessageBox.information(self, "معلومة", "لا يمكن تعديل نقاط التفريع مباشرة")
            return

        narrator, old_method = item

        dialog = QDialog(self)
        dialog.setWindowTitle("تعديل طريقة الرواية")
        dialog.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"الراوي: {narrator.name}"))
        layout.addWidget(QLabel("طريقة الرواية:"))

        method_combo = QComboBox()
        methods = list(NARRATION_METHODS.keys())
        methods.remove('default')
        method_combo.addItems(methods)
        method_combo.setCurrentText(old_method)
        layout.addWidget(method_combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_method = method_combo.currentText()
            self.setUpdatesEnabled(False)
            try:
                self.chain_items[current_row] = (narrator, new_method)
                self.update_chain_list()
                self.draw_chain()
                self.chain_list.setCurrentRow(current_row)
            finally:
                self.setUpdatesEnabled(True)

    def remove_narrator(self):
        """Remove selected item from the list or its node."""
        if not hasattr(self, 'chain_list'):
            return

        selected_items = self.chain_view.scene.selectedItems()
        for item in selected_items:
            if isinstance(item, TextBox):
                self.remove_text_box(item)

        current_item = self.chain_list.currentItem()
        if not current_item:
            selected_nodes = [item for item in selected_items if isinstance(item, NarratorNode)]
            if selected_nodes:
                for node in selected_nodes:
                    self.remove_narrator_by_id(node.narrator_id)
            return

        data = current_item.data(Qt.ItemDataRole.UserRole)
        if data and data[0] == 'NARRATOR':
            self.remove_narrator_by_id(data[1])

    def remove_narrator_by_id(self, narrator_id):
        """Recursively remove narrator and its children from the chain."""
        def remove_recursive(narrators_list, target_id):
            for i, (n, m) in enumerate(narrators_list):
                n_id = n.id if hasattr(n, 'id') else n.get('id')
                if n_id == target_id:
                    del narrators_list[i]
                    return True
                if hasattr(n, 'children') and n.children:
                    if remove_recursive(n.children, target_id):
                        return True
            return False

        self.setUpdatesEnabled(False)
        try:
            for node in self.chain_nodes:
                if node.narrator_id == narrator_id:
                    node.setSelected(False)

            if remove_recursive(self.chain_items, narrator_id):
                if self.pending_parent_id == narrator_id:
                    self.pending_parent_id = None

                self.update_chain_list()
                self.draw_chain()

                if self.pending_parent_id is not None:
                    for n in self.chain_nodes:
                        if n.narrator_id == self.pending_parent_id:
                            n.setPen(QPen(QColor(0, 120, 215), 4, Qt.PenStyle.DashLine))
                            n.setBrush(QBrush(n.color.darker(110)))

                self.main_window.status_label.setText("تم حذف الراوي")
        finally:
            self.setUpdatesEnabled(True)

    def clear_chain(self):
        """Clear the entire chain."""
        reply = QMessageBox.question(
            self,
            "تأكيد المسح",
            "هل أنت متأكد من مسح السند بالكامل؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.setUpdatesEnabled(False)
            try:
                def clear_recursive(narrators_list):
                    for n, m in narrators_list:
                        if hasattr(n, 'children'):
                            clear_recursive(n.children)
                            n.children = []

                clear_recursive(self.chain_items)
                self.chain_items.clear()
                self.update_chain_list()
                if hasattr(self, 'chain_view'):
                    self.chain_view.clear_scene()
                self.main_window.status_label.setText("تم مسح السند")
            finally:
                self.setUpdatesEnabled(True)

    # ── Drawing ───────────────────────────────────────────────────────────────

    def draw_chain(self):
        """Draw the chain visualization, preserving free-floating text boxes."""
        if not hasattr(self, 'chain_view'):
            return

        self.chain_view.setUpdatesEnabled(False)
        try:
            # ── 1. Preserve free TextBox items before clearing ──────────────
            preserved_text_boxes = []
            for item in self.chain_view.scene.items():
                if isinstance(item, TextBox):
                    preserved_text_boxes.append({
                        'x': item.pos().x(),
                        'y': item.pos().y(),
                        'text': item.text_item.toPlainText(),
                        'color': item.brush().color(),
                        'border_color': item.pen().color(),
                        'text_color': item.text_item.defaultTextColor(),
                        'font': QFont(item.text_item.font()),   # copy
                        'width': item.rect().width(),
                        'height': item.rect().height(),
                    })

            # ── 2. Clear scene and reset node list ──────────────────────────
            self.chain_view.clear_scene()
            self.chain_nodes = []
            self._last_branch_node = None

            if not self.chain_items:
                return

            # ── 3. Draw layout ───────────────────────────────────────────────
            layout_style = self.layout_combo.currentIndex()
            if layout_style == 0:
                self.draw_vertical_tree()
            elif layout_style == 1:
                self.draw_horizontal_tree()
            else:
                self.draw_pyramid()

            # ── 4. Restore text boxes ────────────────────────────────────────
            for tb in preserved_text_boxes:
                text_box = TextBox(
                    tb['x'], tb['y'],
                    width=tb['width'], height=tb['height'],
                    text=tb['text'],
                    app_ref=self.main_window
                )
                text_box.setBrush(QBrush(tb['color']))
                text_box.setPen(QPen(tb['border_color'], 2))
                text_box.text_item.setDefaultTextColor(tb['text_color'])
                text_box.text_item.setFont(tb['font'])
                # Re-center text after font restore
                text_rect = text_box.text_item.boundingRect()
                r = text_box.rect()
                text_box.text_item.setPos(
                    (r.width() - text_rect.width()) / 2,
                    (r.height() - text_rect.height()) / 2
                )
                self.chain_view.scene.addItem(text_box)

            # ── 5. Add matn overlay ──────────────────────────────────────────
            self.add_matn_to_scene()

        finally:
            self.chain_view.setUpdatesEnabled(True)

        QTimer.singleShot(100, self.zoom_fit)
        self.main_window.status_label.setText("✅ تم رسم السند")

    def draw_vertical_tree(self):
        """Draw vertical tree layout."""
        self.graph_controller.draw_vertical_tree(
            self.chain_view.scene,
            self.chain_items,
            self.main_window.narrators_dict,
            self.main_window,
            self.show_method_labels.isChecked()
        )

    def draw_horizontal_tree(self):
        """Draw horizontal tree layout."""
        self.graph_controller.draw_horizontal_tree(
            self.chain_view.scene,
            self.chain_items,
            self.main_window.narrators_dict,
            self.main_window,
            self.show_method_labels.isChecked()
        )

    def draw_pyramid(self):
        """Draw pyramid layout."""
        self.graph_controller.draw_pyramid(
            self.chain_view.scene,
            self.chain_items,
            self.main_window.narrators_dict,
            self.main_window,
            self.show_method_labels.isChecked()
        )

    def add_matn_to_scene(self):
        """Add matn text box above the chain."""
        matn = self.matn_input.toPlainText().strip()
        if not matn:
            return

        matn_width = 600
        matn_padding = 15

        temp_text = QGraphicsTextItem()
        temp_text.setTextWidth(matn_width - 2 * matn_padding)
        temp_text.setHtml(f"""
            <div style='font-family: Amiri; font-size: 13px;
                 text-align: center; line-height: 1.8; color: #000;'>
                <b>المتن:</b><br>{matn}
            </div>
        """)
        text_height = temp_text.boundingRect().height()
        matn_height = text_height + 2 * matn_padding
        matn_x = -matn_width / 2
        matn_y = -matn_height - 50

        matn_rect = QGraphicsRectItem(matn_x, matn_y, matn_width, matn_height)
        matn_rect.setBrush(QBrush(QColor(248, 248, 248)))
        matn_rect.setPen(QPen(QColor(150, 150, 150), 2))
        self.chain_view.scene.addItem(matn_rect)

        matn_text = QGraphicsTextItem()
        matn_text.setTextWidth(matn_width - 2 * matn_padding)
        matn_text.setHtml(f"""
            <div style='font-family: Amiri; font-size: 13px;
                 text-align: center; line-height: 1.8; color: #000;'>
                <b>المتن:</b><br>{matn}
            </div>
        """)
        matn_text.setPos(matn_x + matn_padding, matn_y + matn_padding)
        self.chain_view.scene.addItem(matn_text)

    def add_method_label(self, start_node, end_node, method, connection_line=None):
        """Add method label in beige box."""
        if not method or method == 'default':
            return

        method_info = NARRATION_METHODS.get(method, NARRATION_METHODS['default'])

        start_rect = start_node.sceneBoundingRect()
        end_rect = end_node.sceneBoundingRect()
        mid_x = (start_rect.center().x() + end_rect.center().x()) / 2
        mid_y = (start_rect.bottom() + end_rect.top()) / 2

        beige = QColor(245, 245, 220)
        border_color = QColor(180, 170, 150)

        label = QGraphicsTextItem(method)
        label.setDefaultTextColor(QColor(0, 0, 0))
        font = QFont("Amiri", 12, QFont.Weight.Bold)
        label.setFont(font)

        label_rect = label.boundingRect()
        padding = 8
        box_w = label_rect.width() + padding * 2
        box_h = label_rect.height() + padding * 2

        group = QGraphicsItemGroup()
        group.setPos(mid_x - box_w / 2, mid_y - box_h / 2)

        bg = QGraphicsRectItem(0, 0, box_w, box_h, group)
        bg.setBrush(QBrush(beige))
        bg.setPen(QPen(border_color, 1))
        bg.setZValue(0)

        label.setParentItem(group)
        label.setPos((box_w - label_rect.width()) / 2, (box_h - label_rect.height()) / 2)
        label.setZValue(1)
        group.setZValue(10)

        if connection_line is not None:
            connection_line.set_method_label(group, box_w, box_h)
            group.setParentItem(connection_line)
            connection_line.updatePosition()
        else:
            self.chain_view.scene.addItem(group)

    # ── Pending-parent (Add Child) workflow ───────────────────────────────────

    def add_narrator_after_node(self, parent_narrator_id, node):
        """Designate a parent node for the next addition. Toggles on/off."""
        if self.pending_parent_id == parent_narrator_id:
            self.pending_parent_id = None
            self.main_window.status_label.setText("تم إلغاء اختيار العقدة الأب")
        else:
            self.pending_parent_id = parent_narrator_id
            self.main_window.status_label.setText(
                "بانتظار اختيار راوٍ (من اليمين) أو صندوق فارغ (من اليسار) لإضافته تابعاً...")

        self.setUpdatesEnabled(False)
        try:
            for n in self.chain_nodes:
                if self.pending_parent_id is not None and n.narrator_id == self.pending_parent_id:
                    n.setPen(QPen(QColor(0, 120, 215), 4, Qt.PenStyle.DashLine))
                    n.setBrush(QBrush(n.color.darker(110)))
                else:
                    n.setPen(QPen(n.border_color, 2))
                    n.setBrush(QBrush(n.color))
        finally:
            self.setUpdatesEnabled(True)

    def add_branch_from_node(self, narrator_id, node):
        """Deprecated: delegate to add_narrator_after_node."""
        self.add_narrator_after_node(narrator_id, node)

    def add_sub_branch_to_branch(self, branch_index):
        """Add a new sub-branch to an existing branch point."""
        if branch_index < 0 or branch_index >= len(self.chain_items):
            return

        item = self.chain_items[branch_index]
        if not isinstance(item, tuple) or item[0] != 'BRANCH':
            return

        branches = item[1]
        parent_id = item[2] if len(item) > 2 else None
        branches.append([])

        self.setUpdatesEnabled(False)
        try:
            self.chain_items[branch_index] = ('BRANCH', branches, parent_id)
            if branch_index not in self.expanded_branches:
                self.expanded_branches.add(branch_index)
            self.update_chain_list()
            self.draw_chain()
            self.main_window.status_label.setText(f"تم إضافة فرع فرعي جديد (المجموع: {len(branches)} فروع)")
        finally:
            self.setUpdatesEnabled(True)

    def node_is_branch(self, narrator_id):
        """Check if a node is a branch point."""
        for i, item in enumerate(self.chain_items):
            if isinstance(item, tuple) and item[0] == 'BRANCH':
                parent_id = item[2] if len(item) > 2 else None
                if parent_id == narrator_id:
                    return True, i
        return False, None

    def add_blank_box_to_chain(self):
        """Add a blank, editable narrator box to the chain."""
        selected_nodes = [item for item in self.chain_view.scene.selectedItems() if isinstance(item, NarratorNode)]
        if len(selected_nodes) > 1:
            QMessageBox.warning(self, "تنبيه", "لا يمكن إضافة صندوق فارغ عند اختيار أكثر من عقدة واحدة.")
            return

        from models.narrator import Narrator
        blank_id = self._last_blank_id - 1
        self._last_blank_id = blank_id

        blank_narrator = Narrator(
            id=blank_id,
            name='',
            basic_info={},
            jarh_tadil=[],
            is_custom=True
        )
        blank_narrator.blank = True
        self.main_window.narrators_dict[blank_id] = blank_narrator

        method = self.method_combo.currentText()

        self.setUpdatesEnabled(False)
        try:
            if self.pending_parent_id is not None:
                self._add_narrator_to_parent(self.pending_parent_id, blank_narrator, method)
                self.main_window.status_label.setText("تمت إضافة صندوق فارغ تابع")
            else:
                self.chain_items.append((blank_narrator, method))
                self.main_window.status_label.setText("تمت إضافة صندوق فارغ للسند")

            self.update_chain_list()
            self.draw_chain()

            if self.pending_parent_id is not None:
                for n in self.chain_nodes:
                    if n.narrator_id == self.pending_parent_id:
                        n.setPen(QPen(QColor(0, 120, 215), 4, Qt.PenStyle.DashLine))
                        n.setBrush(QBrush(n.color.darker(110)))
        finally:
            self.setUpdatesEnabled(True)

    def add_text_box_to_canvas(self):
        """Add a free-floating text box at the center of the visible area."""
        if not hasattr(self, 'chain_view'):
            return

        visible_rect = self.chain_view.mapToScene(self.chain_view.viewport().rect()).boundingRect()
        center_x = visible_rect.center().x()
        center_y = visible_rect.center().y()

        text_box = TextBox(center_x - 100, center_y - 30, 200, 60, "", self.main_window)
        self.chain_view.scene.addItem(text_box)
        text_box.setSelected(True)
        self.main_window.status_label.setText("تم إضافة صندوق نص - يمكنك تحريكه وتعديله")

    def remove_text_box(self, text_box):
        """Remove text box from scene."""
        if hasattr(self, 'chain_view') and text_box and text_box.scene():
            self.chain_view.scene.removeItem(text_box)

    def on_layout_changed(self):
        """Redraw when layout changes."""
        if self.chain_items:
            self.draw_chain()

    # ── Canvas click ──────────────────────────────────────────────────────────

    def on_canvas_clicked(self):
        """Handle canvas click - clears detail panel only, does NOT cancel pending parent."""
        self.setUpdatesEnabled(False)
        try:
            if hasattr(self, 'graph_selected_name'):
                self.graph_selected_name.setText("لم يتم اختيار راوٍ")
            if hasattr(self, 'graph_basic_text'):
                self.graph_basic_text.clear()
            if hasattr(self, 'graph_comments_text'):
                self.graph_comments_text.clear()
        finally:
            self.setUpdatesEnabled(True)

    # ── Zoom ──────────────────────────────────────────────────────────────────

    def zoom_in(self):
        if hasattr(self, 'chain_view') and self.chain_view.zoom_level < 5.0:
            self.chain_view.scale(1.2, 1.2)
            self.chain_view.zoom_level *= 1.2

    def zoom_out(self):
        if hasattr(self, 'chain_view') and self.chain_view.zoom_level > 0.2:
            self.chain_view.scale(1 / 1.2, 1 / 1.2)
            self.chain_view.zoom_level /= 1.2

    def zoom_reset(self):
        if hasattr(self, 'chain_view'):
            scale_factor = 1.0 / self.chain_view.zoom_level
            self.chain_view.scale(scale_factor, scale_factor)
            self.chain_view.zoom_level = 1.0

    def zoom_fit(self):
        if hasattr(self, 'chain_view') and hasattr(self, 'chain_nodes') and self.chain_nodes:
            rect = self.chain_view.scene.itemsBoundingRect()
            self.chain_view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
            self.chain_view.scale(0.9, 0.9)
            self.chain_view.zoom_level = 0.9

    # ── Details panel ─────────────────────────────────────────────────────────

    def show_narrator_details(self, narrator_id):
        """Show narrator details in the right panel."""
        narrator = self.main_window.narrators_dict.get(narrator_id)
        if not narrator:
            return

        if hasattr(self, 'graph_selected_name'):
            self.graph_selected_name.setText(narrator.name)

        basic_info = narrator.basic_info
        basic_html = "<table style='width:100%;font-family:Traditional Arabic,Amiri;font-size:13px;' cellpadding='5'>"
        for key, value in basic_info.items():
            basic_html += (f"<tr>"
                           f"<td style='color:#000;font-weight:bold;width:40%;background:#f8f8f8;'>{key}</td>"
                           f"<td style='color:#000;'>{value}</td>"
                           f"</tr>")
        basic_html += "</table>"

        if hasattr(self, 'graph_basic_text'):
            self.graph_basic_text.setHtml(
                basic_html if basic_info
                else "<div style='text-align:center;color:#808080;padding:20px;'>لا توجد معلومات</div>")

        jarh_tadil = narrator.jarh_tadil
        comments_html = "<div style='font-family:Traditional Arabic,Amiri;font-size:13px;'>"
        if jarh_tadil:
            for i, item in enumerate(jarh_tadil, 1):
                scholar = item.get('scholar', 'غير معروف')
                comment = item.get('comment', '')
                source = item.get('source', '')
                comments_html += (f"<div style='margin-bottom:15px;padding:10px;"
                                   f"background:#f8f8f8;border-right:3px solid #c0c0c0;'>"
                                   f"<div style='font-weight:bold;color:#000;margin-bottom:5px;'>{i}. {scholar}</div>"
                                   f"<div style='color:#000;'>{comment}</div>")
                if source:
                    comments_html += f"<div style='color:#606060;font-size:12px;margin-top:5px;'>المصدر: {source}</div>"
                comments_html += "</div>"
        else:
            comments_html += "<div style='text-align:center;color:#808080;padding:20px;'>لا توجد تعليقات</div>"
        comments_html += "</div>"

        if hasattr(self, 'graph_comments_text'):
            self.graph_comments_text.setHtml(comments_html)

    # ── Export ────────────────────────────────────────────────────────────────

    def export_image(self, format='png'):
        if not hasattr(self, 'chain_view') or not self.chain_nodes:
            QMessageBox.warning(self, "تحذير", "لا توجد شجرة لتصديرها")
            return
        self.export_controller.export_image(self.chain_view, self.hadith_name.text(), format)
        self.main_window.status_label.setText("✅ تم حفظ الصورة")

    def export_pdf(self):
        if not hasattr(self, 'chain_view') or not self.chain_nodes:
            QMessageBox.warning(self, "تحذير", "لا توجد شجرة لتصديرها")
            return
        self.export_controller.export_pdf(self.chain_view, self.hadith_name.text())
        self.main_window.status_label.setText("✅ تم حفظ PDF")

    def copy_canvas_to_clipboard(self):
        if not hasattr(self, 'chain_view'):
            QMessageBox.warning(self, "تحذير", "لا توجد لوحة لنسخها")
            return
        self.export_controller.copy_to_clipboard(self.chain_view)
        self.main_window.status_label.setText("✅ تم نسخ الصورة إلى الحافظة")

    def save_chain(self):
        if not self.chain_items:
            QMessageBox.warning(self, "تحذير", "لا يوجد سند لحفظه")
            return
        data = {
            'hadith_name': self.hadith_name.text(),
            'matn': self.matn_input.toPlainText(),
            'layout_style': self.layout_combo.currentIndex(),
            'created': datetime.now().isoformat()
        }
        self.export_controller.save_chain(self.chain_items, data, self.main_window.narrators_dict,
                                          self.chain_view.scene)
        self.main_window.status_label.setText("✅ تم حفظ السند")

    # ── Clipboard (node copy/paste) ───────────────────────────────────────────

    def copy_to_clipboard(self):
        selected_nodes = [item for item in self.chain_view.scene.selectedItems() if isinstance(item, NarratorNode)]
        if not selected_nodes:
            return
        node = selected_nodes[0]
        narrator = self.main_window.narrators_dict.get(node.narrator_id)
        if narrator:
            import copy
            self._clipboard_data = copy.deepcopy(narrator)
            self._clipboard_method = node.method
            self.main_window.status_label.setText(f"تم نسخ: {node.narrator_name}")

    def cut_to_clipboard(self):
        selected_nodes = [item for item in self.chain_view.scene.selectedItems() if isinstance(item, NarratorNode)]
        if not selected_nodes:
            return
        self.copy_to_clipboard()
        for node in selected_nodes:
            self.remove_narrator_by_id(node.narrator_id)

    def paste_from_clipboard(self):
        if not hasattr(self, '_clipboard_data'):
            return
        import copy
        narrator = copy.deepcopy(self._clipboard_data)
        if hasattr(narrator, 'id') and narrator.id < 0:
            self._last_custom_id -= 1
            narrator.id = self._last_custom_id
            self.main_window.narrators_dict[narrator.id] = narrator

        method = getattr(self, '_clipboard_method', 'عن')

        self.setUpdatesEnabled(False)
        try:
            if self.pending_parent_id is not None:
                self._add_narrator_to_parent(self.pending_parent_id, narrator, method)
            else:
                self.chain_items.append((narrator, method))
            self.update_chain_list()
            self.draw_chain()
            self.main_window.status_label.setText(f"تم لصق: {narrator.name}")
        finally:
            self.setUpdatesEnabled(True)

    # ── Load chain ────────────────────────────────────────────────────────────

    def load_chain(self):
        """Load chain from file."""
        chain_items, data = self.export_controller.load_chain(self.main_window.narrators_dict)
        if not chain_items:
            return

        self.setUpdatesEnabled(False)
        try:
            self.hadith_name.setText(data.get('hadith_name', ''))
            self.matn_input.setPlainText(data.get('matn', ''))
            self.layout_combo.setCurrentIndex(data.get('layout_style', 0))

            self.chain_items = chain_items
            self.update_chain_list()
            self.draw_chain()

            # Restore saved text boxes
            if 'text_boxes' in data:
                for tb_data in data['text_boxes']:
                    text_box = TextBox(
                        tb_data.get('x', 0),
                        tb_data.get('y', 0),
                        width=tb_data.get('width', 200),
                        height=tb_data.get('height', 60),
                        text=tb_data.get('text', ''),
                        app_ref=self.main_window
                    )
                    self.chain_view.scene.addItem(text_box)

                    if 'color' in tb_data:
                        text_box.setBrush(QBrush(QColor(tb_data['color'])))
                    if 'border_color' in tb_data:
                        text_box.setPen(QPen(QColor(tb_data['border_color']), 2))
                    if 'text_color' in tb_data:
                        text_box.text_item.setDefaultTextColor(QColor(tb_data['text_color']))

                    font = text_box.text_item.font()
                    if 'font_size' in tb_data:
                        font.setPointSize(tb_data['font_size'])
                    if 'bold' in tb_data:
                        font.setBold(tb_data['bold'])
                    if 'italic' in tb_data:
                        font.setItalic(tb_data['italic'])
                    text_box.text_item.setFont(font)

                    text_rect = text_box.text_item.boundingRect()
                    r = text_box.rect()
                    text_box.text_item.setPos(
                        (r.width() - text_rect.width()) / 2,
                        (r.height() - text_rect.height()) / 2
                    )

            self.main_window.status_label.setText("✅ تم تحميل السند")
        finally:
            self.setUpdatesEnabled(True)