"""
Narrator data model.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class Narrator:
    """Represents a hadith narrator."""
    id: int
    name: str
    basic_info: Dict[str, str] = field(default_factory=dict)
    jarh_tadil: List[Dict[str, str]] = field(default_factory=list)
    is_custom: bool = False
    url: str = ""
    children: List[Any] = field(default_factory=list) # List of (Narrator, method)

    def to_dict(self) -> Dict[str, Any]:
        """Convert narrator to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'basic_info': self.basic_info,
            'jarh_tadil': self.jarh_tadil,
            'is_custom': self.is_custom,
            'url': self.url
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Narrator':
        """Create narrator from dictionary."""
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            basic_info=data.get('basic_info', {}),
            jarh_tadil=data.get('jarh_tadil', []),
            is_custom=data.get('is_custom', False),
            url=data.get('url', '')
        )

    def get_search_text(self) -> str:
        """Get searchable text for this narrator."""
        parts = [self.name]
        parts.extend(self.basic_info.values())
        for j in self.jarh_tadil:
            parts.append(j.get('scholar', ''))
            parts.append(j.get('comment', ''))
        return ' '.join(str(p) for p in parts if p)