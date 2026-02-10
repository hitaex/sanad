#!/bin/bash
# Launcher script for Sanad

# Change to the script directory
cd "$(dirname "$0")"

# Set Qt platform if needed (for Wayland/X11 compatibility)
if [ -z "$QT_QPA_PLATFORM" ]; then
    export QT_QPA_PLATFORM=xcb  # Force X11 for compatibility
fi

# Set scaling for HiDPI displays
export QT_AUTO_SCREEN_SCALE_FACTOR=1
export QT_SCALE_FACTOR=1
export QT_FONT_DPI=96

# Run the application
exec ./sanad
