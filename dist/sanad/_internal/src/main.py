#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Combined Hadith Chain Visualization Application.

This application provides:
- Search and browsing of narrator database
- Visual chain (isnad) construction
- Branch support for multiple narration paths
- Export to PNG/PDF
- Custom narrator creation
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from main_window import CombinedHadithApp


def main():
    """Main function entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Set RTL layout for Arabic
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    window = CombinedHadithApp()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())