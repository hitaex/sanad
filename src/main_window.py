"""
Main application window.
"""

import sys
import os
import json
import queue
import threading
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import TABAQAT_OPTIONS, NARRATION_METHODS, debug_print
from models.database import DatabaseManager
from models.narrator import Narrator
from models.chain import Chain, ChainItem
from ui.search_tab import SearchTab
from ui.books_tab import BooksTab
from ui.graph_tab import GraphTab
from ui.credits_tab import CreditsTab
from ui.settings_tab import SettingsTab
from ui.dialogs.custom_narrator_dialog import create_custom_narrator_dialog
from ui.base_widgets import ResizableSplitter
from utils.theme import apply_theme
from controllers.export_controller import ExportController
class CombinedHadithApp(QMainWindow):
    """Main application combining search and graphing."""

    def __init__(self):
        super().__init__()
        debug_print("CombinedHadithApp.__init__: Initializing")

        # Data storage
        self.narrators = []
        self.narrators_dict = {}
        self.loaded_count = 0
        self.current_narrator = None

        # Chain data
        self.chain_items = []
        self.chain_nodes = []
        self.expanded_branches = set()
        self.active_branch_index = None
        self.active_sub_branch = 0

        # Threading
        self.loading_queue = queue.Queue()
        self.loading_thread = None

        # Database
        self.db = DatabaseManager()

        # Setup UI
        self.setup_ui()
        apply_theme(self)

        # Start loading data
        self.start_loading_data()

    def setup_ui(self):
        """Setup the combined interface with tabs."""
        self.setWindowTitle("تراجم عبد الله العنزي - البحث ورسم الأسانيد")
        self.setGeometry(100, 100, 1600, 900)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create header
        self.create_header(main_layout)

        # Create toolbar
        self.create_toolbar(main_layout)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("mainTabs")

        search_tab = SearchTab(self)
        graph_tab = GraphTab(self)
        books_tab = BooksTab(self)
        credits_tab = CreditsTab(self)
        settings_tab = SettingsTab(self)

        self.tab_widget.addTab(search_tab, "🔍 البحث في الرواة")
        self.tab_widget.addTab(graph_tab, "🌳 رسم السند")
        self.tab_widget.addTab(books_tab, "📚 الكتب")
        self.tab_widget.addTab(settings_tab, "⚙️ الإعدادات")
        self.tab_widget.addTab(credits_tab, "ℹ️ حول البرنامج")
        main_layout.addWidget(self.tab_widget, 1)

        # Create status bar
        self.create_status_bar()

    def set_dark_mode(self, is_dark):
        """Set application theme to bright or dark mode."""
        apply_theme(self, is_dark)
        # Update all tabs if needed (canvas should stay white as per request)
        # The GraphTab's graphics view has its background set to white explicitly in its __init__ or scene setup.
        self.status_label.setText(f"تم تفعيل النمط {'الداكن' if is_dark else 'الفاتح'}")

    def create_header(self, parent_layout):
        """Create header section."""
        header = QFrame()
        header.setFixedHeight(80)
        header.setObjectName("header")

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 15, 10)

        title_frame = QFrame()
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)

        # Try to load image as logo
        logo_loaded = False
        if os.path.exists('image_1.png'):
            pixmap = QPixmap('image_1.png')
            if not pixmap.isNull():
                pixmap = pixmap.scaled(400, 60, Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
                logo_label = QLabel()
                logo_label.setPixmap(pixmap)
                title_layout.addWidget(logo_label)
                logo_loaded = True

        if not logo_loaded:
            title_label = QLabel("معجم الرواة - تصميم أبي دحيم العنزي")
            title_label.setObjectName("appTitle")
            title_layout.addWidget(title_label)
        title_layout.addStretch()
        header_layout.addWidget(title_frame)

        parent_layout.addWidget(header)

    def create_toolbar(self, parent_layout):
        """Create toolbar section."""
        toolbar = QFrame()
        toolbar.setFixedHeight(45)
        toolbar.setObjectName("toolbar")

        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        toolbar_layout.setSpacing(5)

        toolbar_buttons = [
            ("📄", "ملف جديد"),
            ("📂", "فتح"),
            ("💾", "حفظ"),
            ("🖨️", "طباعة"),
            ("✂️", "قص"),
            ("📋", "نسخ"),
            ("📌", "لصق"),
            ("🔍", "بحث"),
            ("⬅️", "تراجع"),
            ("➡️", "إعادة"),
        ]

        for icon, tooltip in toolbar_buttons:
            btn = QPushButton(icon)
            btn.setObjectName("toolbarButton")
            btn.setToolTip(tooltip)
            btn.setFixedSize(35, 35)
            if tooltip == "فتح":
                btn.clicked.connect(lambda: self.tab_widget.widget(1).load_chain())
            elif tooltip == "حفظ":
                btn.clicked.connect(lambda: self.tab_widget.widget(1).save_chain())
            toolbar_layout.addWidget(btn)

        toolbar_layout.addStretch()
        parent_layout.addWidget(toolbar)

    def create_status_bar(self):
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_label = QLabel("جاهز")
        self.status_bar.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setObjectName("progressBar")
        self.status_bar.addWidget(self.progress_bar)
        self.progress_bar.hide()

    def start_loading_data(self):
        """Start loading data from JSON directories in background."""

        def load_data():
            try:
                debug_print("Loading narrators from JSON directories...")
                
                narrators = self.db.get_all_narrators()
                self.loaded_count = len(narrators)
                
                for narrator in narrators:
                    self.narrators.append(narrator)
                    self.narrators_dict[narrator.id] = narrator
                
                debug_print(f"Loaded {self.loaded_count} narrators from JSON.")
                self.loading_queue.put(("complete", self.loaded_count))

            except Exception as e:
                self.loading_queue.put(("error", f"❌ خطأ في التحميل: {str(e)}"))

        self.loading_thread = threading.Thread(target=load_data, daemon=True)
        self.loading_thread.start()

        self.load_timer = QTimer()
        self.load_timer.timeout.connect(self.check_loading_queue)
        self.load_timer.start(100)

    def load_from_db(self):
        """Helper to load data from database."""
        pass

    def check_loading_queue(self):
        """Check loading queue."""
        try:
            while True:
                msg_type, data = self.loading_queue.get_nowait()

                if msg_type == "progress":
                    loaded, total = data
                    self.status_label.setText(f"جارٍ التحميل... {loaded:,}/{total:,}")
                    self.progress_bar.show()
                    self.progress_bar.setRange(0, total)
                    self.progress_bar.setValue(loaded)

                elif msg_type == "complete":
                    self.load_timer.stop()
                    self.progress_bar.hide()
                    self.status_label.setText(f"✅ تم تحميل {data:,} راوٍ")

                    # Enable search button
                    search_tab = self.tab_widget.widget(0)
                    if hasattr(search_tab, 'set_narrators'):
                        search_tab.set_narrators(self.narrators)
                    elif hasattr(search_tab, 'search_btn'):
                        search_tab.search_btn.setEnabled(True)

                    # Populate narrator list for graphing tab
                    graph_tab = self.tab_widget.widget(1)
                    if hasattr(graph_tab, 'populate_narrator_list'):
                        graph_tab.populate_narrator_list(self.narrators)

                elif msg_type == "error":
                    self.load_timer.stop()
                    self.progress_bar.hide()
                    self.status_label.setText(data)

        except queue.Empty:
            pass

    # Chain methods
    def node_has_main_child(self, narrator_id):
        """Check if node has main child in graph tab."""
        graph_tab = self.tab_widget.widget(1)
        if not hasattr(graph_tab, 'chain_items'):
            return False
            
        node_index = None
        for i, item in enumerate(graph_tab.chain_items):
            if isinstance(item, tuple) and item[0] != 'BRANCH':
                n, _ = item
                # Handle both Narrator object and dict
                n_id = n.id if hasattr(n, 'id') else n.get('id')
                if n_id == narrator_id:
                    node_index = i
                    break
        if node_index is None:
            return False
        next_idx = node_index + 1
        if next_idx >= len(graph_tab.chain_items):
            return False
        next_item = graph_tab.chain_items[next_idx]
        return isinstance(next_item, tuple) and next_item[0] != 'BRANCH'

    def node_is_branch(self, narrator_id):
        """Check if a node is actually a branch point in graph tab."""
        graph_tab = self.tab_widget.widget(1)
        if not hasattr(graph_tab, 'chain_items'):
            return False, None
            
        for i, item in enumerate(graph_tab.chain_items):
            if isinstance(item, tuple) and item[0] == 'BRANCH':
                parent_id = item[2] if len(item) > 2 else None
                if parent_id == narrator_id:
                    return True, i
        return False, None

    def add_narrator_after_node(self, parent_narrator_id, node):
        """Add narrator after node."""
        graph_tab = self.tab_widget.widget(1)
        if hasattr(graph_tab, 'add_narrator_after_node'):
            graph_tab.add_narrator_after_node(parent_narrator_id, node)

    def add_branch_from_node(self, narrator_id, node):
        """Add branch from node."""
        graph_tab = self.tab_widget.widget(1)
        if hasattr(graph_tab, 'add_branch_from_node'):
            graph_tab.add_branch_from_node(narrator_id, node)

    def add_sub_branch_to_branch(self, branch_index):
        """Add sub-branch to existing branch."""
        graph_tab = self.tab_widget.widget(1)
        if hasattr(graph_tab, 'add_sub_branch_to_branch'):
            graph_tab.add_sub_branch_to_branch(branch_index)

    def add_method_label(self, start_node, end_node, method, connection_line=None):
        """Proxy for GraphTab.add_method_label."""
        graph_tab = self.tab_widget.widget(1)
        if hasattr(graph_tab, 'add_method_label'):
            graph_tab.add_method_label(start_node, end_node, method, connection_line)

    def on_graph_node_double_clicked(self, narrator_id):
        """Handle node double-click."""
        narrator = self.narrators_dict.get(narrator_id)
        if not narrator:
            return

        # Show in graph tab details
        graph_tab = self.tab_widget.widget(1)
        if hasattr(graph_tab, 'show_narrator_details'):
            graph_tab.show_narrator_details(narrator_id)

        # Switch to details tab
        if hasattr(graph_tab, 'right_tabs'):
            graph_tab.right_tabs.setCurrentIndex(1)

    def on_canvas_clicked(self):
        """Handle canvas click."""
        graph_tab = self.tab_widget.widget(1)
        if hasattr(graph_tab, 'on_canvas_clicked'):
            graph_tab.on_canvas_clicked()

    def remove_text_box(self, text_box):
        """Remove text box from scene."""
        graph_tab = self.tab_widget.widget(1)
        if hasattr(graph_tab, 'remove_text_box'):
            graph_tab.remove_text_box(text_box)

    def remove_narrator_by_id(self, narrator_id):
        """Remove narrator by ID from graph tab."""
        graph_tab = self.tab_widget.widget(1)
        if hasattr(graph_tab, 'remove_narrator_by_id'):
            graph_tab.remove_narrator_by_id(narrator_id)

    def on_node_text_changed(self, narrator_id, new_name):
        """Handle node text change."""
        # Update in dictionary if it's there
        if narrator_id in self.narrators_dict:
            narrator = self.narrators_dict[narrator_id]
            if hasattr(narrator, 'name'):
                narrator.name = new_name
            elif isinstance(narrator, dict):
                narrator['name'] = new_name

    def on_graph_node_hovered(self, narrator_name):
        """Handle node hover."""
        self.status_label.setText(f"الراوي: {narrator_name}")

    def on_graph_node_hover_ended(self, narrator_name):
        """Handle node hover end."""
        pass

    def create_custom_narrator(self):
        """Create custom narrator."""
        from ui.dialogs.custom_narrator_dialog import create_custom_narrator_dialog
        narrator = create_custom_narrator_dialog(self, self.db)
        if narrator:
            self.narrators.append(narrator)
            self.narrators_dict[narrator.id] = narrator

            # Refresh narrator list in graph tab
            graph_tab = self.tab_widget.widget(1)
            if hasattr(graph_tab, 'populate_narrator_list'):
                graph_tab.populate_narrator_list(self.narrators)

            self.status_label.setText(f"✅ تم إنشاء الراوي: {narrator.name}")