"""
Theme application for Wikipedia-style monochrome theme.
"""


def apply_theme(app, is_dark=False):
    """Apply Wikipedia-style monochrome theme (Bright or Dark)."""
    if not is_dark:
        # Bright Theme (Original Wikipedia style)
        app.setStyleSheet("""
            QMainWindow {
                background-color: #f8f8f8;
            }

            #header {
                background-color: #ffffff;
                border-bottom: 1px solid #c0c0c0;
            }

            #appTitle {
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 16px;
                font-weight: normal;
                color: #000000;
                padding: 5px;
            }

            #toolbar {
                background-color: #f0f0f0;
                border-bottom: 1px solid #c0c0c0;
            }

            #toolbarButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 2px;
                padding: 3px;
                font-size: 14px;
            }

            #toolbarButton:hover {
                background-color: #e0e0e0;
                border: 1px solid #c0c0c0;
            }

            #mainTabs::pane {
                border: 1px solid #c0c0c0;
                background-color: #ffffff;
            }

            QTabBar::tab {
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 13px;
                background-color: #e0e0e0;
                border: 1px solid #c0c0c0;
                border-bottom: none;
                padding: 8px 16px;
                color: #000000;
            }

            QTabBar::tab:selected {
                background-color: #ffffff;
                font-weight: bold;
            }

            QTabBar::tab:hover {
                background-color: #f0f0f0;
            }

            #sidePanel {
                background-color: #f0f0f0;
                border-left: 1px solid #c0c0c0;
                border-right: 1px solid #c0c0c0;
            }

            #panelHeader {
                background-color: #e0e0e0;
                border-bottom: 1px solid #c0c0c0;
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 14px;
                font-weight: bold;
                color: #000000;
                padding: 5px;
            }

            #centerPanel {
                background-color: #ffffff;
            }

            #searchFrame {
                background-color: #f8f8f8;
                border-bottom: 1px solid #c0c0c0;
            }

            #searchLabel {
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 13px;
                color: #000000;
                font-weight: bold;
            }

            #searchInput {
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 13px;
                background-color: white;
                border: 1px solid #a0a0a0;
                padding: 5px;
                color: #000000;
            }

            #searchInput:focus {
                border: 1px solid #0078d7;
            }

            #resultsHeader {
                background-color: #f0f0f0;
                border-top: 1px solid #c0c0c0;
                border-bottom: 1px solid #c0c0c0;
            }

            #resultsCount {
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 13px;
                color: #000000;
                font-weight: bold;
            }

            #resultsTable {
                background-color: white;
                border: 1px solid #c0c0c0;
                gridline-color: #e0e0e0;
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 13px;
                color: #000000;
                selection-background-color: #0078d7;
                selection-color: white;
            }

            #resultsTable::item {
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
            }

            QHeaderView::section {
                background-color: #e0e0e0;
                color: #000000;
                padding: 8px;
                border: none;
                border-right: 1px solid #c0c0c0;
                border-bottom: 1px solid #c0c0c0;
                font-weight: bold;
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 13px;
            }

            #detailsSection {
                background-color: #ffffff;
                border: 1px solid #c0c0c0;
                border-radius: 0px;
            }

            #selectedName {
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 15px;
                font-weight: bold;
                color: #000000;
                padding: 5px;
            }

            #sectionTitle {
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 13px;
                font-weight: bold;
                color: #000000;
                padding: 5px;
                background-color: #f0f0f0;
                border-bottom: 1px solid #c0c0c0;
            }

            #detailsText {
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 13px;
                background-color: white;
                color: #000000;
                border: none;
                line-height: 1.6;
            }

            #inputField {
                font-family: 'Amiri', 'Traditional Arabic', Arial;
                font-size: 13px;
                background-color: #ffffff;
                border: 1px solid #a0a0a0;
                padding: 4px;
                color: #000000;
            }

            #inputField:focus {
                border: 1px solid #606060;
            }

            #primaryButton {
                font-family: 'Amiri', 'Traditional Arabic', Arial;
                font-size: 13px;
                background-color: #e0e0e0;
                border: 1px solid #a0a0a0;
                padding: 8px;
                color: #000000;
                font-weight: bold;
            }

            #primaryButton:hover {
                background-color: #d0d0d0;
            }

            #actionButton {
                font-family: 'Amiri', 'Traditional Arabic', Arial;
                font-size: 12px;
                background-color: #f0f0f0;
                border: 1px solid #a0a0a0;
                padding: 6px 12px;
                color: #000000;
            }

            #actionButton:hover {
                background-color: #e0e0e0;
            }

            #actionButton:disabled {
                background-color: #f8f8f8;
                color: #a0a0a0;
            }

            #chainList, #narratorList {
                font-family: 'Amiri', 'Traditional Arabic', Arial;
                font-size: 13px;
                background-color: #ffffff;
                border: 1px solid #a0a0a0;
                color: #000000;
            }

            #chainList::item, #narratorList::item {
                padding: 6px;
                border-bottom: 1px solid #e0e0e0;
            }

            #chainList::item:selected, #narratorList::item:selected {
                background-color: #c0c0c0;
                color: #000000;
            }

            QStatusBar {
                background-color: #f0f0f0;
                color: #000000;
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 12px;
                border-top: 1px solid #c0c0c0;
            }

            #progressBar {
                border: 1px solid #a0a0a0;
                border-radius: 0px;
                text-align: center;
                color: #000000;
                background-color: white;
            }

            #progressBar::chunk {
                background-color: #0078d7;
            }
        """)
    else:
        # Dark Theme
        app.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }

            #header {
                background-color: #252525;
                border-bottom: 1px solid #444444;
            }

            #appTitle {
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 16px;
                font-weight: normal;
                color: #ffffff;
                padding: 5px;
            }

            #toolbar {
                background-color: #2d2d2d;
                border-bottom: 1px solid #444444;
            }

            #toolbarButton {
                background-color: #3d3d3d;
                border: 1px solid #555555;
                border-radius: 2px;
                padding: 3px;
                font-size: 14px;
                color: #ffffff;
            }

            #toolbarButton:hover {
                background-color: #4d4d4d;
                border: 1px solid #666666;
            }

            #mainTabs::pane {
                border: 1px solid #444444;
                background-color: #252525;
            }

            QTabBar::tab {
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 13px;
                background-color: #2d2d2d;
                border: 1px solid #444444;
                border-bottom: none;
                padding: 8px 16px;
                color: #b0b0b0;
            }

            QTabBar::tab:selected {
                background-color: #252525;
                color: #ffffff;
                font-weight: bold;
            }

            QTabBar::tab:hover {
                background-color: #353535;
            }

            #sidePanel {
                background-color: #252525;
                border-left: 1px solid #444444;
                border-right: 1px solid #444444;
            }

            #panelHeader {
                background-color: #2d2d2d;
                border-bottom: 1px solid #444444;
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
                padding: 5px;
            }

            #centerPanel {
                background-color: #1e1e1e;
            }

            #searchFrame {
                background-color: #252525;
                border-bottom: 1px solid #444444;
            }

            #searchLabel {
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 13px;
                color: #ffffff;
                font-weight: bold;
            }

            #searchInput {
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 13px;
                background-color: #2d2d2d;
                border: 1px solid #555555;
                padding: 5px;
                color: #ffffff;
            }

            #searchInput:focus {
                border: 1px solid #0078d7;
            }

            #resultsHeader {
                background-color: #2d2d2d;
                border-top: 1px solid #444444;
                border-bottom: 1px solid #444444;
            }

            #resultsCount {
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 13px;
                color: #ffffff;
                font-weight: bold;
            }

            #resultsTable {
                background-color: #252525;
                border: 1px solid #444444;
                gridline-color: #333333;
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 13px;
                color: #e0e0e0;
                selection-background-color: #004a80;
                selection-color: white;
            }

            #resultsTable::item {
                padding: 8px;
                border-bottom: 1px solid #333333;
            }

            QHeaderView::section {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px;
                border: none;
                border-right: 1px solid #444444;
                border-bottom: 1px solid #444444;
                font-weight: bold;
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 13px;
            }

            #detailsSection {
                background-color: #252525;
                border: 1px solid #444444;
                border-radius: 0px;
            }

            #selectedName {
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 15px;
                font-weight: bold;
                color: #ffffff;
                padding: 5px;
            }

            #sectionTitle {
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 13px;
                font-weight: bold;
                color: #ffffff;
                padding: 5px;
                background-color: #2d2d2d;
                border-bottom: 1px solid #444444;
            }

            #detailsText {
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 13px;
                background-color: #252525;
                color: #e0e0e0;
                border: none;
                line-height: 1.6;
            }

            #inputField {
                font-family: 'Amiri', 'Traditional Arabic', Arial;
                font-size: 13px;
                background-color: #2d2d2d;
                border: 1px solid #555555;
                padding: 4px;
                color: #ffffff;
            }

            #inputField:focus {
                border: 1px solid #0078d7;
            }

            #primaryButton, #branchButton, #drawButton {
                font-family: 'Amiri', 'Traditional Arabic', Arial;
                font-size: 13px;
                background-color: #e0e0e0;
                border: 1px solid #a0a0a0;
                padding: 8px;
                color: #000000;
                font-weight: bold;
            }

            #primaryButton:hover, #branchButton:hover, #drawButton:hover {
                background-color: #d0d0d0;
            }

            #actionButton {
                font-family: 'Amiri', 'Traditional Arabic', Arial;
                font-size: 12px;
                background-color: #f0f0f0;
                border: 1px solid #a0a0a0;
                padding: 6px 12px;
                color: #000000;
            }

            #actionButton:hover {
                background-color: #e0e0e0;
            }

            #actionButton:disabled {
                background-color: #252525;
                color: #666666;
            }

            #chainList, #narratorList {
                font-family: 'Amiri', 'Traditional Arabic', Arial;
                font-size: 13px;
                background-color: #252525;
                border: 1px solid #555555;
                color: #e0e0e0;
            }

            #chainList::item, #narratorList::item {
                padding: 6px;
                border-bottom: 1px solid #333333;
            }

            #chainList::item:selected, #narratorList::item:selected {
                background-color: #3d3d3d;
                color: #ffffff;
            }

            QStatusBar {
                background-color: #2d2d2d;
                color: #e0e0e0;
                font-family: 'Traditional Arabic', 'Amiri', 'Segoe UI', Arial;
                font-size: 12px;
                border-top: 1px solid #444444;
            }

            #progressBar {
                border: 1px solid #555555;
                border-radius: 0px;
                text-align: center;
                color: #ffffff;
                background-color: #2d2d2d;
            }

            #progressBar::chunk {
                background-color: #0078d7;
            }

            QLabel {
                color: #e0e0e0;
            }

            QComboBox, QSpinBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 4px;
            }

            QTextEdit, QTextBrowser {
                background-color: #252525;
                color: #e0e0e0;
                border: 1px solid #555555;
            }

            /* Buttons inside viewports/tabs should stay light if they are standard buttons, 
               but user asked to keep "buttons and canvas" bright. 
               We target StyledPushButton and normal QPushButton that don't have specific IDs.
            */
            QPushButton:not(#toolbarButton):not(#primaryButton):not(#actionButton) {
                background-color: #f0f0f0;
                color: #000000;
                border: 1px solid #a0a0a0;
            }

            /* Credits introduction text color in dark mode */
            #detailsSection QLabel {
                color: #e0e0e0;
            }
        """)