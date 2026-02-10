"""
Search tab UI component.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import rapidfuzz
from controllers.search_controller import SearchController
from ui.base_widgets import ResizableSplitter
from config import TABAQAT_OPTIONS


class SearchTab(QWidget):
    """Search tab for narrator search and browsing."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.search_controller = None
        self._last_search_results = []
        self._last_search_query = ""
        self.setup_ui()

    def setup_ui(self):
        """Setup search tab UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create panels
        center_panel = self.create_center_panel()
        left_panel = self.create_left_panel()

        # Use splitter for resizable panels
        splitter = ResizableSplitter(Qt.Orientation.Horizontal)
        splitter.addWidgetWithStretch(center_panel, 5)
        splitter.addWidgetWithStretch(left_panel, 3, min_width=300, max_width=500)
        layout.addWidget(splitter)

    def create_center_panel(self):
        """Create center results panel."""
        panel = QFrame()
        panel.setObjectName("centerPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Search section
        search_frame = QFrame()
        search_frame.setObjectName("searchFrame")
        search_frame.setFixedHeight(125)

        search_layout = QVBoxLayout(search_frame)
        search_layout.setContentsMargins(15, 10, 15, 10)
        search_layout.setSpacing(8)

        # Search label
        search_label = QLabel("البحث في فهارس الرواة")
        search_label.setObjectName("searchLabel")
        search_layout.addWidget(search_label)

        # Search controls row
        search_controls = QHBoxLayout()
        search_controls.setSpacing(10)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("اكتب اسم الراوي أو الكنية...")
        self.search_input.setObjectName("searchInput")
        self.search_input.setFixedHeight(32)
        self.search_input.returnPressed.connect(self.perform_search)
        search_controls.addWidget(self.search_input, 3)

        # Search type combo
        self.search_type = QComboBox()
        self.search_type.addItems(["بحث تقريبي", "بحث دقيق"])
        self.search_type.setObjectName("searchCombo")
        self.search_type.setFixedWidth(120)
        search_controls.addWidget(self.search_type)

        # Result limit
        self.result_limit = QSpinBox()
        self.result_limit.setRange(10, 200)
        self.result_limit.setValue(50)
        self.result_limit.setObjectName("searchSpin")
        self.result_limit.setFixedWidth(80)
        search_controls.addWidget(self.result_limit)

        # Search button
        self.search_btn = QPushButton("🔍 ابحث")
        self.search_btn.setObjectName("searchButton")
        self.search_btn.setFixedWidth(100)
        self.search_btn.clicked.connect(self.perform_search)
        self.search_btn.setEnabled(False)
        search_controls.addWidget(self.search_btn)

        search_layout.addLayout(search_controls)

        # Filter by طبقة
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("تصفية حسب الطبقة:"))
        self.tabaqa_filter = QComboBox()
        self.tabaqa_filter.addItems(TABAQAT_OPTIONS)
        self.tabaqa_filter.setObjectName("tabaqaFilter")
        self.tabaqa_filter.setFixedWidth(180)
        self.tabaqa_filter.currentTextChanged.connect(self._apply_tabaqa_filter_to_results)
        filter_row.addWidget(self.tabaqa_filter)
        filter_row.addStretch()
        search_layout.addLayout(filter_row)

        layout.addWidget(search_frame)

        # Results header
        results_header = QFrame()
        results_header.setObjectName("resultsHeader")
        results_header.setFixedHeight(35)

        header_layout = QHBoxLayout(results_header)
        header_layout.setContentsMargins(15, 5, 15, 5)

        self.results_count = QLabel("عدد النتائج: 0")
        self.results_count.setObjectName("resultsCount")
        header_layout.addWidget(self.results_count)
        header_layout.addStretch()

        layout.addWidget(results_header)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setObjectName("resultsTable")
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "اسم الراوي",
            "الكنية",
            "تاريخ الوفاة",
            "الرتبة عند ابن حجر",
            "عدد التعليقات"
        ])

        # Set column widths
        self.results_table.setColumnWidth(0, 280)
        self.results_table.setColumnWidth(1, 150)
        self.results_table.setColumnWidth(2, 120)
        self.results_table.setColumnWidth(3, 180)
        self.results_table.setColumnWidth(4, 120)

        self.results_table.horizontalHeader().setStretchLastSection(False)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setShowGrid(True)
        self.results_table.verticalHeader().setVisible(True)
        self.results_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.results_table.doubleClicked.connect(self.on_result_double_click)

        layout.addWidget(self.results_table, 1)

        return panel

    def create_left_panel(self):
        """Create left details panel."""
        panel = QFrame()
        panel.setObjectName("sidePanel")
        panel.setFixedWidth(380)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Panel header
        header = QLabel("تفاصيل الراوي")
        header.setObjectName("panelHeader")
        header.setFixedHeight(35)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Details content
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(10, 10, 10, 10)
        details_layout.setSpacing(10)

        # Name section
        name_frame = QFrame()
        name_frame.setObjectName("detailsSection")
        name_layout = QVBoxLayout(name_frame)
        name_layout.setContentsMargins(10, 10, 10, 10)

        self.selected_name = QLabel("لم يتم اختيار راوٍ")
        self.selected_name.setObjectName("selectedName")
        self.selected_name.setWordWrap(True)
        name_layout.addWidget(self.selected_name)

        details_layout.addWidget(name_frame)

        # Basic info section
        info_frame = QFrame()
        info_frame.setObjectName("detailsSection")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(10, 10, 10, 10)

        info_title = QLabel("المعلومات الأساسية")
        info_title.setObjectName("sectionTitle")
        info_layout.addWidget(info_title)

        self.basic_text = QTextBrowser()
        self.basic_text.setObjectName("detailsText")
        info_layout.addWidget(self.basic_text, 1)

        details_layout.addWidget(info_frame, 1)

        # Comments section
        comments_frame = QFrame()
        comments_frame.setObjectName("detailsSection")
        comments_layout = QVBoxLayout(comments_frame)
        comments_layout.setContentsMargins(10, 10, 10, 10)

        comments_title = QLabel("الجرح والتعديل")
        comments_title.setObjectName("sectionTitle")
        comments_layout.addWidget(comments_title)

        self.comments_text = QTextBrowser()
        self.comments_text.setObjectName("detailsText")
        comments_layout.addWidget(self.comments_text, 1)

        details_layout.addWidget(comments_frame, 2)

        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.copy_btn = QPushButton("📋 نسخ")
        self.copy_btn.setObjectName("actionButton")
        self.copy_btn.setEnabled(False)
        self.copy_btn.clicked.connect(self.copy_data)
        buttons_layout.addWidget(self.copy_btn)

        self.browser_btn = QPushButton("🌐 فتح")
        self.browser_btn.setObjectName("actionButton")
        self.browser_btn.setEnabled(False)
        self.browser_btn.clicked.connect(self.open_in_browser)
        buttons_layout.addWidget(self.browser_btn)

        self.save_btn = QPushButton("💾 حفظ")
        self.save_btn.setObjectName("actionButton")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_to_file)
        buttons_layout.addWidget(self.save_btn)

        details_layout.addLayout(buttons_layout)

        # Scroll area for details
        scroll = QScrollArea()
        scroll.setObjectName("detailsScroll")
        scroll.setWidget(details_widget)
        scroll.setWidgetResizable(True)

        layout.addWidget(scroll, 1)

        return panel

    def set_narrators(self, narrators):
        """Set narrators data and initialize search controller."""
        self.narrators = narrators
        self.search_controller = SearchController(narrators)
        self.search_btn.setEnabled(True)

    def perform_search(self):
        """Perform search."""
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.information(self, "تنبيه", "الرجاء إدخال نص للبحث")
            return

        if not self.search_controller:
            QMessageBox.warning(self, "تنبيه", "محرك البحث غير جاهز!")
            return

        # Clear results
        self.results_table.setRowCount(0)

        # Get search parameters
        search_type = self.search_type.currentIndex()
        limit = self.result_limit.value()

        # Perform search
        results = self.search_controller.search_narrators(query, search_type, limit)
        self._last_search_results = results
        self._last_search_query = query

        # Apply طبقة filter then display
        results = self._filter_results_by_tabaqa(results)

        # Display results
        self.results_table.setRowCount(len(results))

        for row, narrator in enumerate(results):
            name = narrator.name
            basic_info = narrator.basic_info
            
            # The new schema stores basic_info as a dict
            kunya = basic_info.get('الكنية', basic_info.get('الاسم', '-'))
            death_date = basic_info.get('تاريخ الوفاة', '-')
            rank = basic_info.get('الرتبة عند ابن حجر', '-')
            comment_count = len(narrator.jarh_tadil)

            # Create table items
            items = [
                QTableWidgetItem(name),
                QTableWidgetItem(kunya),
                QTableWidgetItem(death_date),
                QTableWidgetItem(rank),
                QTableWidgetItem(str(comment_count))
            ]

            # Add items to table
            for col, item in enumerate(items):
                item.setData(Qt.ItemDataRole.UserRole, narrator.id)
                self.results_table.setItem(row, col, item)

        # Update count
        self.results_count.setText(f"عدد النتائج: {len(results)}")

    def _filter_results_by_tabaqa(self, results):
        """Filter results by selected طبقة."""
        tabaqa = self.tabaqa_filter.currentText()
        if tabaqa == "الجميع":
            return results
        if tabaqa == "خارج طبقات التقريب":
            return [n for n in results if not n.basic_info.get('طبقة رواة التقريب', '').strip()]
        return [n for n in results if n.basic_info.get('طبقة رواة التقريب', '') == tabaqa]

    def _apply_tabaqa_filter_to_results(self):
        """Re-apply طبقة filter to last search results."""
        if not hasattr(self, '_last_search_results'):
            return
        results = self._filter_results_by_tabaqa(self._last_search_results)
        self.results_table.setRowCount(len(results))
        for row, narrator in enumerate(results):
            name = narrator.name
            basic_info = narrator.basic_info
            
            kunya = basic_info.get('الكنية', basic_info.get('الاسم', '-'))
            death_date = basic_info.get('تاريخ الوفاة', '-')
            rank = basic_info.get('الرتبة عند ابن حجر', '-')
            comment_count = len(narrator.jarh_tadil)
            
            for col, item in enumerate([
                QTableWidgetItem(name),
                QTableWidgetItem(kunya),
                QTableWidgetItem(death_date),
                QTableWidgetItem(rank),
                QTableWidgetItem(str(comment_count))
            ]):
                item.setData(Qt.ItemDataRole.UserRole, narrator.id)
                self.results_table.setItem(row, col, item)
        self.results_count.setText(f"عدد النتائج: {len(results)}")

    def on_selection_changed(self):
        """Handle selection change in results table."""
        selected_items = self.results_table.selectedItems()
        if selected_items:
            narrator_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.show_narrator_details(narrator_id)

    def on_result_double_click(self, index):
        """Handle double click on result."""
        row = index.row()
        item = self.results_table.item(row, 0)
        if item:
            narrator_id = item.data(Qt.ItemDataRole.UserRole)
            self.show_narrator_details(narrator_id)

    def show_narrator_details(self, narrator_id):
        """Show narrator details in left panel."""
        narrator = self.main_window.narrators_dict.get(narrator_id)
        if not narrator:
            return

        self.main_window.current_narrator = narrator

        # Update name
        self.selected_name.setText(narrator.name)

        # Update basic info
        basic_info = narrator.basic_info
        basic_html = "<table style='width: 100%; font-family: Traditional Arabic, Amiri; font-size: 13px;' cellpadding='5'>"

        for key, value in basic_info.items():
            basic_html += f"<tr>"
            basic_html += f"<td style='color: #000000; font-weight: bold; width: 40%; background-color: #f8f8f8;'>{key}</td>"
            basic_html += f"<td style='color: #000000;'>{value}</td>"
            basic_html += f"</tr>"

        basic_html += "</table>"

        self.basic_text.setHtml(
            basic_html if basic_info else "<div style='text-align: center; color: #808080; padding: 20px;'>لا توجد معلومات</div>")

        # Update comments
        jarh_tadil = narrator.jarh_tadil
        comments_html = "<div style='font-family: Traditional Arabic, Amiri; font-size: 13px;'>"

        if jarh_tadil:
            for i, item in enumerate(jarh_tadil, 1):
                scholar = item.get('scholar', 'غير معروف')
                comment = item.get('comment', '')
                source = item.get('source', '')

                comments_html += f"<div style='margin-bottom: 15px; padding: 10px; background-color: #f8f8f8; border-right: 3px solid #c0c0c0;'>"
                comments_html += f"<div style='font-weight: bold; color: #000000; margin-bottom: 5px;'>{i}. {scholar}</div>"
                comments_html += f"<div style='color: #000000;'>{comment}</div>"

                if source:
                    comments_html += f"<div style='color: #606060; font-size: 12px; margin-top: 5px;'>المصدر: {source}</div>"

                comments_html += "</div>"
        else:
            comments_html += "<div style='text-align: center; color: #808080; padding: 20px;'>لا توجد تعليقات</div>"

        comments_html += "</div>"
        self.comments_text.setHtml(comments_html)

        # Enable buttons
        self.copy_btn.setEnabled(True)
        self.browser_btn.setEnabled(bool(narrator.url))
        self.save_btn.setEnabled(True)

    def copy_data(self):
        """Copy narrator data to clipboard."""
        if not self.main_window.current_narrator:
            return

        try:
            narrator = self.main_window.current_narrator
            text = f"الاسم: {narrator.name}\n"
            text += f"الرقم: {narrator.id}\n\n"

            basic_info = narrator.basic_info
            if basic_info:
                text += "المعلومات الأساسية:\n"
                for key, value in basic_info.items():
                    text += f"{key}: {value}\n"
                text += "\n"

            jarh_tadil = narrator.jarh_tadil
            if jarh_tadil:
                text += "الجرح والتعديل:\n"
                for i, item in enumerate(jarh_tadil, 1):
                    text += f"{i}. {item.get('scholar', '')}: {item.get('comment', '')}\n"

            clipboard = QApplication.clipboard()
            clipboard.setText(text)

            self.main_window.status_label.setText("✅ تم نسخ البيانات")
        except Exception as e:
            self.main_window.status_label.setText(f"❌ خطأ: {str(e)}")

    def open_in_browser(self):
        """Open narrator URL in browser."""
        if not self.main_window.current_narrator:
            return

        url = self.main_window.current_narrator.url
        if url:
            try:
                import webbrowser
                webbrowser.open(url)
                self.main_window.status_label.setText("✅ تم فتح الرابط")
            except:
                self.main_window.status_label.setText("❌ تعذر فتح المتصفح")
        else:
            self.main_window.status_label.setText("⚠️ لا يوجد رابط")

    def save_to_file(self):
        """Save narrator data to file."""
        if not self.main_window.current_narrator:
            return

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "حفظ ملف الراوي",
            f"راوي_{self.main_window.current_narrator.id}.json",
            "ملفات JSON (*.json);;ملفات نصية (*.txt)"
        )

        if file_name:
            try:
                import json
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(self.main_window.current_narrator.to_dict(), f, ensure_ascii=False, indent=2)

                self.main_window.status_label.setText(f"✅ تم حفظ الملف")
            except Exception as e:
                self.main_window.status_label.setText(f"❌ خطأ في الحفظ")