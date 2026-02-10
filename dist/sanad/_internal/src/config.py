"""
Configuration constants for the Hadith application.
"""

import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

# Debug mode
DEBUG_MODE = '--debug' in sys.argv


def debug_print(*args, **kwargs):
    """Print debug messages if debug mode is enabled"""
    if DEBUG_MODE:
        print(f"[DEBUG] {' '.join(str(a) for a in args)}", **kwargs)


# طبقات رواة التقريب (12 + خارج)
TABAQAT_OPTIONS = [
    "الجميع",
    "الأولى",
    "الثانية",
    "الثالثة",
    "الرابعة",
    "الخامسة",
    "السادسة",
    "السابعة",
    "الثامنة",
    "التاسعة",
    "العاشرة",
    "الحادية عشرة",
    "الثانية عشرة",
    "خارج طبقات التقريب",
]


# Narration method definitions with GREEN-TO-RED color grading
def get_color_for_strength(strength):
    """Convert strength (1-5) to green-to-red color"""
    if strength >= 5:
        return QColor(0, 200, 0)
    if strength >= 4:
        return QColor(100, 200, 0)
    if strength >= 3:
        return QColor(200, 200, 0)
    if strength >= 2:
        return QColor(200, 150, 0)
    return QColor(200, 0, 0)


NARRATION_METHODS = {
    # Explicit hearing methods (صيغ صريحة في السماع) - Strength 5 = Green
    'سمعت': {'color': get_color_for_strength(5), 'label': 'سماع مباشر', 'strength': 5, 'thickness': 4},
    'سمعنا': {'color': get_color_for_strength(5), 'label': 'سماع مباشر', 'strength': 5, 'thickness': 4},
    'حدثني': {'color': get_color_for_strength(5), 'label': 'تحديث مباشر', 'strength': 5, 'thickness': 4},
    'حدثنا': {'color': get_color_for_strength(5), 'label': 'تحديث مباشر', 'strength': 5, 'thickness': 4},
    'أخبرني': {'color': get_color_for_strength(5), 'label': 'إخبار مباشر', 'strength': 5, 'thickness': 4},
    'أخبرنا': {'color': get_color_for_strength(5), 'label': 'إخبار مباشر', 'strength': 5, 'thickness': 4},

    # Reading methods (القراءة) - Strength 4 = Yellow-green
    'قرأت عليه': {'color': get_color_for_strength(4), 'label': 'قراءة على الشيخ', 'strength': 4, 'thickness': 3},
    'قرأنا عليه': {'color': get_color_for_strength(4), 'label': 'قراءة على الشيخ', 'strength': 4, 'thickness': 3},
    'قرئ عليه وأنا أسمع': {'color': get_color_for_strength(4), 'label': 'قراءة بحضور', 'strength': 4, 'thickness': 3},
    'قرئ عليه': {'color': get_color_for_strength(4), 'label': 'قراءة بحضور', 'strength': 4, 'thickness': 3},

    # Authorization methods (الإجازة) - Strength 3 = Yellow
    'أخبرني إجازة': {'color': get_color_for_strength(3), 'label': 'إجازة', 'strength': 3, 'thickness': 2},
    'حدثني إجازة': {'color': get_color_for_strength(3), 'label': 'إجازة', 'strength': 3, 'thickness': 2},
    'أجاز لي': {'color': get_color_for_strength(3), 'label': 'إجازة', 'strength': 3, 'thickness': 2},
    'أنبأنا': {'color': get_color_for_strength(3), 'label': 'إنباء', 'strength': 3, 'thickness': 2},
    'أنبأني': {'color': get_color_for_strength(3), 'label': 'إنباء', 'strength': 3, 'thickness': 2},

    # Ambiguous methods (صيغ محتملة) - Strength 2 = Orange
    'عن': {'color': get_color_for_strength(2), 'label': 'عنعنة (محتمل)', 'strength': 2, 'thickness': 2},
    'قال': {'color': get_color_for_strength(2), 'label': 'قول (محتمل)', 'strength': 2, 'thickness': 2},
    'عن طريق': {'color': get_color_for_strength(2), 'label': 'عنعنة', 'strength': 2, 'thickness': 2},

    # Weak/disconnected methods (صيغ منقطعة) - Strength 1 = Red
    'بلغني': {'color': get_color_for_strength(1), 'label': 'منقطع', 'strength': 1, 'thickness': 1},
    'حُدثت': {'color': get_color_for_strength(1), 'label': 'منقطع', 'strength': 1, 'thickness': 1},
    'قيل': {'color': get_color_for_strength(1), 'label': 'منقطع', 'strength': 1, 'thickness': 1},
    'روي': {'color': get_color_for_strength(1), 'label': 'منقطع', 'strength': 1, 'thickness': 1},

    # Default
    'default': {'color': QColor(150, 150, 150), 'label': 'غير محدد', 'strength': 0, 'thickness': 2}
}