"""
Branch dialog for adding branch points.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class BranchDialog(QDialog):
    """Dialog for adding branch points."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة تفريع (ح)")
        self.setMinimumWidth(300)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("عدد الفروع (يمكن إضافة أكثر من 10):"))

        self.branch_count = QSpinBox()
        self.branch_count.setRange(1, 20)  # Allow up to 20 branches
        self.branch_count.setValue(2)
        layout.addWidget(self.branch_count)

        layout.addWidget(QLabel("سيتم إنشاء (ح) مع الفروع المحددة"))

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_branch_count(self):
        """Get selected branch count."""
        return self.branch_count.value()