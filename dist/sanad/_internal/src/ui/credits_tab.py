"""
Credits tab for the application.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class CreditsTab(QWidget):
    """Credits tab showing contributors and theme toggle."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        """Setup credits tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Credits Content
        credits_frame = QFrame()
        credits_frame.setObjectName("detailsSection")
        credits_layout = QVBoxLayout(credits_frame)
        credits_layout.setContentsMargins(40, 40, 40, 40)
        credits_layout.setSpacing(20)

        title_label = QLabel("حول البرنامج")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; font-family: 'Traditional Arabic', 'Amiri';")
        credits_layout.addWidget(title_label)

        intro_label = QLabel(
            "هذا البرنامج مخصص لمساعدة الباحثين في علم الحديث على تصور سلاسل الرواة (الأسانيد) بشكل تفاعلي. "
            "يتيح البرنامج البحث في قاعدة بيانات واسعة للرواة، وتكوين شجرات أسانيد معقدة، وتصديرها كصور أو ملفات PDF."
        )
        intro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        intro_label.setWordWrap(True)
        intro_label.setStyleSheet("font-size: 16px; font-family: 'Traditional Arabic', 'Amiri'; color: #555555;")
        credits_layout.addWidget(intro_label)

        names_label = QLabel("حقوق العمل: عبد الله العنزي، أبو دحيم")
        names_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        names_label.setStyleSheet("font-size: 20px; font-family: 'Traditional Arabic', 'Amiri';")
        credits_layout.addWidget(names_label)

        design_label = QLabel("Design & calligraphy: أ. الفيفي")
        design_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        design_label.setStyleSheet("font-size: 18px; font-family: 'Traditional Arabic', 'Amiri';")
        credits_layout.addWidget(design_label)

        layout.addWidget(credits_frame)

        # Bottom Button
        bottom_button = QPushButton("إغلاق")
        bottom_button.setObjectName("primaryButton")
        bottom_button.setFixedWidth(200)
        bottom_button.clicked.connect(lambda: self.main_window.tab_widget.setCurrentIndex(0))
        layout.addWidget(bottom_button, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

    def on_theme_toggled(self):
        """DEPRECATED: Dark mode toggle removed."""
        pass
