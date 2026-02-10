"""
Helper functions for the application.
"""

import os
import json
from typing import Dict, Any


def ensure_directory(directory):
    """Ensure directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def load_json_file(filepath):
    """Load JSON file with error handling."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def save_json_file(filepath, data):
    """Save data to JSON file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving {filepath}: {e}")
        return False


def format_narrator_info(narrator: Dict[str, Any]) -> str:
    """Format narrator information for display."""
    if not narrator:
        return "لا توجد معلومات"

    text = f"الاسم: {narrator.get('name', 'غير معروف')}\n"
    text += f"الرقم: {narrator.get('id', '')}\n\n"

    basic_info = narrator.get('basic_info', {})
    if basic_info:
        text += "المعلومات الأساسية:\n"
        for key, value in basic_info.items():
            text += f"{key}: {value}\n"
        text += "\n"

    jarh_tadil = narrator.get('jarh_tadil', [])
    if jarh_tadil:
        text += "الجرح والتعديل:\n"
        for i, item in enumerate(jarh_tadil, 1):
            text += f"{i}. {item.get('scholar', '')}: {item.get('comment', '')}\n"

    return text


def validate_narrator_data(data: Dict[str, Any]) -> bool:
    """Validate narrator data structure."""
    required_fields = ['name']

    for field in required_fields:
        if field not in data or not data[field]:
            return False

    # Validate basic_info if present
    if 'basic_info' in data and not isinstance(data['basic_info'], dict):
        return False

    # Validate jarh_tadil if present
    if 'jarh_tadil' in data:
        if not isinstance(data['jarh_tadil'], list):
            return False
        for item in data['jarh_tadil']:
            if not isinstance(item, dict):
                return False

    return True


def get_unique_id(existing_ids, start_id=-10000):
    """Generate a unique negative ID."""
    current_id = start_id
    while current_id in existing_ids:
        current_id -= 1
    return current_id


def truncate_text(text, max_length=100):
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def sanitize_filename(filename):
    """Sanitize filename for safe saving."""
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Limit length
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200 - len(ext)] + ext

    return filename