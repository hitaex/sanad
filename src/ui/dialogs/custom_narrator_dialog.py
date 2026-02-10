"""
Custom narrator creation dialog.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from models.narrator import Narrator
from config import TABAQAT_OPTIONS

def create_custom_narrator_dialog(parent, db):
    """Open dialog to create a custom narrator."""
    dialog = QDialog(parent)
    dialog.setWindowTitle("إنشاء راوٍ جديد")
    dialog.setMinimumWidth(700)
    dialog.setMinimumHeight(800)
    dialog.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    main_layout = QVBoxLayout(dialog)
    main_layout.setSpacing(15)

    # Scroll area
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setObjectName("detailsScroll")

    scroll_widget = QWidget()
    layout = QVBoxLayout(scroll_widget)
    layout.setSpacing(12)

    # Name (Required)
    layout.addWidget(QLabel("<b>الاسم الكامل (إجباري):</b>"))
    name_input = QLineEdit()
    name_input.setObjectName("inputField")
    name_input.setPlaceholderText("مثال: محمد بن عبد الله")
    layout.addWidget(name_input)

    # Kunya
    layout.addWidget(QLabel("الكنية:"))
    kunya_input = QLineEdit()
    kunya_input.setObjectName("inputField")
    kunya_input.setPlaceholderText("مثال: أبو عبد الله")
    layout.addWidget(kunya_input)

    # Nasab
    layout.addWidget(QLabel("النسب:"))
    nasab_input = QLineEdit()
    nasab_input.setObjectName("inputField")
    nasab_input.setPlaceholderText("مثال: القرشي الهاشمي")
    layout.addWidget(nasab_input)

    # Laqab
    layout.addWidget(QLabel("اللقب:"))
    laqab_input = QLineEdit()
    laqab_input.setObjectName("inputField")
    laqab_input.setPlaceholderText("مثال: الصديق")
    layout.addWidget(laqab_input)

    # Tabaqa
    layout.addWidget(QLabel("الطبقة:"))
    tabaqa_combo = QComboBox()
    tabaqa_combo.setObjectName("methodCombo")
    tabaqa_options = [opt for opt in TABAQAT_OPTIONS if opt != "الجميع"]
    tabaqa_combo.addItems(tabaqa_options)
    layout.addWidget(tabaqa_combo)

    # Death date
    layout.addWidget(QLabel("تاريخ الوفاة:"))
    death_input = QLineEdit()
    death_input.setObjectName("inputField")
    death_input.setPlaceholderText("مثال: 110 هـ")
    layout.addWidget(death_input)

    # Ibn Hajar rank
    layout.addWidget(QLabel("الرتبة عند ابن حجر:"))
    rank_input = QLineEdit()
    rank_input.setObjectName("inputField")
    rank_input.setPlaceholderText("مثال: ثقة حافظ")
    layout.addWidget(rank_input)

    # Scholar sayings
    layout.addWidget(QLabel("<b>أقوال العلماء في الراوي:</b>"))
    layout.addWidget(QLabel("<small>يمكنك إضافة عدة أقوال لعلماء مختلفين</small>"))

    scholar_sayings_container = QWidget()
    scholar_sayings_layout = QVBoxLayout(scholar_sayings_container)
    scholar_sayings_layout.setSpacing(10)
    scholar_sayings_layout.setContentsMargins(0, 0, 0, 0)

    scholar_sayings = []

    def add_scholar_saying():
        saying_frame = QFrame()
        saying_frame.setObjectName("detailsSection")
        saying_frame.setStyleSheet("QFrame#detailsSection { background-color: #f5f5f5; border: 1px solid #ccc; padding: 8px; }")
        saying_layout = QVBoxLayout(saying_frame)
        saying_layout.setContentsMargins(10, 10, 10, 10)
        saying_layout.setSpacing(8)

        saying_layout.addWidget(QLabel("اسم العالِم:"))
        scholar_name = QLineEdit()
        scholar_name.setObjectName("inputField")
        scholar_name.setPlaceholderText("مثال: الذهبي")
        saying_layout.addWidget(scholar_name)

        saying_layout.addWidget(QLabel("القول:"))
        comment = QTextEdit()
        comment.setObjectName("inputField")
        comment.setPlaceholderText("مثال: ثقة متقن...")
        comment.setMaximumHeight(100)
        saying_layout.addWidget(comment)

        saying_layout.addWidget(QLabel("<b>المصدر (إجباري):</b>"))
        source = QLineEdit()
        source.setObjectName("inputField")
        source.setPlaceholderText("مثال: تهذيب الكمال 15/234")
        saying_layout.addWidget(source)

        delete_btn = QPushButton("🗑️ حذف هذا القول")
        delete_btn.setObjectName("actionButton")
        delete_btn.clicked.connect(lambda: remove_scholar_saying(saying_frame))
        saying_layout.addWidget(delete_btn)

        scholar_sayings.append({
            'frame': saying_frame,
            'scholar': scholar_name,
            'comment': comment,
            'source': source
        })

        scholar_sayings_layout.addWidget(saying_frame)

    def remove_scholar_saying(frame):
        for i, saying in enumerate(scholar_sayings):
            if saying['frame'] == frame:
                scholar_sayings_layout.removeWidget(frame)
                frame.deleteLater()
                scholar_sayings.pop(i)
                break

    layout.addWidget(scholar_sayings_container)

    add_saying_btn = QPushButton("➕ إضافة قول عالِم")
    add_saying_btn.setObjectName("primaryButton")
    add_saying_btn.clicked.connect(add_scholar_saying)
    layout.addWidget(add_saying_btn)

    add_scholar_saying()

    scroll.setWidget(scroll_widget)
    main_layout.addWidget(scroll)

    # Dialog buttons
    buttons = QDialogButtonBox()
    create_btn = buttons.addButton("✅ إنشاء الراوي", QDialogButtonBox.ButtonRole.AcceptRole)
    create_btn.setObjectName("primaryButton")
    cancel_btn = buttons.addButton("إلغاء", QDialogButtonBox.ButtonRole.RejectRole)
    cancel_btn.setObjectName("actionButton")
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    main_layout.addWidget(buttons)

    # Execute dialog
    if dialog.exec() == QDialog.DialogCode.Accepted:
        name = name_input.text().strip()
        if not name:
            QMessageBox.warning(parent, "تحذير", "الرجاء إدخال اسم الراوي")
            return None

        jarh_tadil = []
        for saying in scholar_sayings:
            scholar = saying['scholar'].text().strip()
            comment = saying['comment'].toPlainText().strip()
            source = saying['source'].text().strip()

            if scholar or comment:
                if not source:
                    QMessageBox.warning(
                        parent,
                        "تحذير",
                        "المصدر إجباري لكل قول عالِم.\n\n"
                        "إذا لم يكن لديك مصدر، احذف القول أو أضف مصدراً."
                    )
                    return None

                jarh_tadil.append({
                    'scholar': scholar,
                    'comment': comment,
                    'source': source
                })

        # Save to database
        narrator = Narrator(
            id=0,  # Will be set by database
            name=name,
            basic_info={},
            jarh_tadil=jarh_tadil,
            is_custom=True
        )

        if name:
            narrator.basic_info['الاسم'] = name
        if kunya_input.text().strip():
            narrator.basic_info['الكنية'] = kunya_input.text().strip()
        if nasab_input.text().strip():
            narrator.basic_info['النسب'] = nasab_input.text().strip()
        if laqab_input.text().strip():
            narrator.basic_info['اللقب'] = laqab_input.text().strip()
        if tabaqa_combo.currentText() and tabaqa_combo.currentText() != "خارج طبقات التقريب":
            narrator.basic_info['طبقة رواة التقريب'] = tabaqa_combo.currentText()
        if death_input.text().strip():
            narrator.basic_info['تاريخ الوفاة'] = death_input.text().strip()
        if rank_input.text().strip():
            narrator.basic_info['الرتبة عند ابن حجر'] = rank_input.text().strip()

        narrator_id = db.save_custom_narrator(narrator)
        narrator.id = narrator_id

        return narrator

    return None