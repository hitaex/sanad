"""
Settings tab for the application.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from models.narrator import Narrator

class SettingsTab(QWidget):
    """Settings tab for managing application behavior and custom narrators."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        """Setup settings tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header_label = QLabel("⚙️ الإعدادات")
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; font-family: 'Traditional Arabic', 'Amiri';")
        layout.addWidget(header_label)

        # Custom Narrators Section
        custom_group = QGroupBox("الرواة المخصصون")
        custom_group.setStyleSheet("font-size: 18px; font-weight: bold; font-family: 'Traditional Arabic', 'Amiri';")
        custom_layout = QVBoxLayout(custom_group)

        self.custom_list = QListWidget()
        self.custom_list.setObjectName("narratorList")
        self.custom_list.setStyleSheet("font-size: 14px;")
        custom_layout.addWidget(self.custom_list)

        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 تحديث القائمة")
        self.refresh_btn.setObjectName("actionButton")
        self.refresh_btn.clicked.connect(self.load_custom_narrators)
        btn_layout.addWidget(self.refresh_btn)

        self.save_temp_btn = QPushButton("💾 حفظ الرواة المؤقتين في المجلد المخصص")
        self.save_temp_btn.setObjectName("primaryButton")
        self.save_temp_btn.setToolTip("حفظ الرواة الذين تم إنشاؤهم خلال هذه الجلسة بشكل دائم في مجلد JSON")
        self.save_temp_btn.clicked.connect(self.save_temp_to_json)

        custom_layout.addLayout(btn_layout)
        layout.addWidget(custom_group, 1)

        # Info Section
        info_group = QGroupBox("معلومات النظام")
        info_layout = QVBoxLayout(info_group)
        
        self.data_info_label = QLabel(f"مجلد البيانات المخصصة: {self.main_window.db.custom_dir}")
        info_layout.addWidget(self.data_info_label)
        
        self.stats_label = QLabel("عدد الرواة الإجمالي: 0")
        info_layout.addWidget(self.stats_label)

        layout.addWidget(info_group)
        
        layout.addStretch()

    def load_custom_narrators(self):
        """Load custom narrators from JSON and current session."""
        self.custom_list.clear()
        
        # 1. From JSON
        json_custom = self.main_window.db.get_custom_narrators()
        for n in json_custom:
            item = QListWidgetItem(f"🏠 {n.name} (في المجلد المخصص)")
            item.setData(Qt.ItemDataRole.UserRole, n)
            self.custom_list.addItem(item)
            
        # 2. From Session (not yet in JSON)
        json_ids = {n.id for n in json_custom}
        for n in self.main_window.narrators:
            if n.is_custom and n.id not in json_ids:
                item = QListWidgetItem(f"✨ {n.name} (مؤقت)")
                item.setData(Qt.ItemDataRole.UserRole, n)
                self.custom_list.addItem(item)

        self.stats_label.setText(f"عدد الرواة الإجمالي: {len(self.main_window.narrators)}")

    def save_temp_to_json(self):
        """Save session custom narrators to JSON."""
        json_custom = self.main_window.db.get_custom_narrators()
        json_ids = {n.id for n in json_custom}
        
        count = 0
        for n in self.main_window.narrators:
            if n.is_custom and n.id not in json_ids:
                try:
                    # save_custom_narrator will assign a real positive ID if needed.
                    old_id = n.id
                    new_id = self.main_window.db.save_custom_narrator(n)
                    
                    # Update the narrator in the main list and dictionary with the new ID
                    if old_id != new_id:
                        if old_id in self.main_window.narrators_dict:
                            del self.main_window.narrators_dict[old_id]
                        n.id = new_id
                        self.main_window.narrators_dict[new_id] = n
                    
                    count += 1
                except Exception as e:
                    print(f"Error saving {n.name}: {e}")
        
        if count > 0:
            QMessageBox.information(self, "نجاح", f"تم حفظ {count} راوٍ في المجلد المخصص بنجاح.")
            # Refresh the list in GraphTab as well
            graph_tab = self.main_window.tab_widget.widget(1)
            if hasattr(graph_tab, 'populate_narrator_list'):
                graph_tab.populate_narrator_list(self.main_window.narrators)
            self.load_custom_narrators()
        else:
            QMessageBox.information(self, "تنبيه", "لا يوجد رواة مؤقتون جدد لحفظهم.")

    def showEvent(self, event):
        """Update list when tab is shown."""
        super().showEvent(event)
        self.load_custom_narrators()
