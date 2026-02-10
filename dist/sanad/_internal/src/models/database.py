"""
JSON data management for narrators.
"""

import json
import os
from typing import List, Dict, Optional
from .narrator import Narrator


class DatabaseManager:
    """Manages JSON-based data operations for narrators.
    Maintains the name DatabaseManager for compatibility.
    """

    def __init__(self, db_path=None):
        # We ignore db_path as we now use JSON directories
        self.main_dir = "Data/JSON/narrators"
        self.custom_dir = "Data/JSON/custom_narrators"
        
        # Ensure directories exist
        for directory in [self.main_dir, self.custom_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

    def get_narrator_by_id(self, narrator_id: int) -> Optional[Narrator]:
        """Get narrator by ID searching both directories."""
        # Check custom first
        custom_path = os.path.join(self.custom_dir, f"{narrator_id}.json")
        if os.path.exists(custom_path):
            return self._load_from_file(custom_path)
            
        # Check main
        main_path = os.path.join(self.main_dir, f"{narrator_id}.json")
        if os.path.exists(main_path):
            return self._load_from_file(main_path)
            
        return None

    def _load_from_file(self, filepath: str) -> Optional[Narrator]:
        """Helper to load a Narrator from a JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Narrator.from_dict(data)
        except Exception:
            return None

    def get_all_narrators(self) -> List[Narrator]:
        """Get all narrators from both directories."""
        narrators = []
        
        # Load from main
        if os.path.exists(self.main_dir):
            for filename in os.listdir(self.main_dir):
                if filename.endswith(".json"):
                    n = self._load_from_file(os.path.join(self.main_dir, filename))
                    if n:
                        narrators.append(n)
                    
        # Load from custom
        if os.path.exists(self.custom_dir):
            for filename in os.listdir(self.custom_dir):
                if filename.endswith(".json"):
                    n = self._load_from_file(os.path.join(self.custom_dir, filename))
                    if n:
                        narrators.append(n)
                    
        return sorted(narrators, key=lambda x: x.name)

    def get_custom_narrators(self) -> List[Narrator]:
        """Get only custom narrators."""
        narrators = []
        if os.path.exists(self.custom_dir):
            for filename in os.listdir(self.custom_dir):
                if filename.endswith(".json"):
                    n = self._load_from_file(os.path.join(self.custom_dir, filename))
                    if n:
                        narrators.append(n)
        return sorted(narrators, key=lambda x: x.name)

    def save_custom_narrator(self, narrator: Narrator) -> int:
        """Save a narrator to the custom JSON directory."""
        # Handle ID if it's 0 (new narrator)
        if narrator.id == 0 or narrator.id is None:
            # Generate a new ID based on custom folder files
            existing_ids = []
            if os.path.exists(self.custom_dir):
                for filename in os.listdir(self.custom_dir):
                    if filename.endswith(".json"):
                        try:
                            # Strip .json and convert to int
                            name_part = filename[:-5]
                            existing_ids.append(int(name_part))
                        except ValueError:
                            continue
            
            if not existing_ids:
                narrator.id = 100000  # Starting ID for custom narrators
            else:
                narrator.id = max(existing_ids) + 1
        
        filepath = os.path.join(self.custom_dir, f"{narrator.id}.json")
        
        # Ensure is_custom is True
        narrator.is_custom = True
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(narrator.to_dict(), f, ensure_ascii=False, indent=2)
            return narrator.id
        except Exception:
            return 0

    def close(self):
        """No-op for JSON manager."""
        pass
