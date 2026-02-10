"""
Chain data model for hadith isnad visualization.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Any
from models.narrator import Narrator


@dataclass
class ChainItem:
    """Represents an item in the chain."""
    narrator: Narrator
    method: str
    is_branch: bool = False
    branch_data: Optional[List[List[Tuple[Narrator, str]]]] = None
    parent_id: Optional[int] = None

    def to_tuple(self):
        """Convert to tuple format for backward compatibility."""
        if self.is_branch and self.branch_data:
            return ('BRANCH', self.branch_data, self.parent_id)
        return (self.narrator, self.method)

    @classmethod
    def from_tuple(cls, item_tuple):
        """Create from tuple format."""
        if isinstance(item_tuple, tuple) and item_tuple[0] == 'BRANCH':
            return cls(
                narrator=Narrator(id=0, name="BRANCH"),
                method='',
                is_branch=True,
                branch_data=item_tuple[1],
                parent_id=item_tuple[2] if len(item_tuple) > 2 else None
            )
        else:
            narrator, method = item_tuple
            return cls(narrator=narrator, method=method)


@dataclass
class Chain:
    """Represents a complete hadith chain."""
    items: List[ChainItem] = field(default_factory=list)
    hadith_name: str = ""
    matn: str = ""
    layout_style: int = 0  # 0=vertical, 1=horizontal, 2=pyramid

    def add_narrator(self, narrator: Narrator, method: str):
        """Add narrator to chain."""
        item = ChainItem(narrator=narrator, method=method)
        self.items.append(item)

    def add_branch(self, branches: List[List[Tuple[Narrator, str]]], parent_id: Optional[int] = None):
        """Add branch point to chain."""
        item = ChainItem(
            narrator=Narrator(id=0, name="BRANCH"),
            method='',
            is_branch=True,
            branch_data=branches,
            parent_id=parent_id
        )
        self.items.append(item)

    def to_dict(self) -> Dict[str, Any]:
        """Convert chain to dictionary for saving."""
        chain_data = []
        for item in self.items:
            if item.is_branch and item.branch_data:
                branch_narrators = []
                if item.branch_data and item.branch_data[0]:
                    for n, method in item.branch_data[0]:
                        branch_narrators.append({
                            'narrator_id': n.id,
                            'narrator_name': n.name,
                            'method': method
                        })
                chain_data.append({'type': 'BRANCH', 'branch': branch_narrators})
            else:
                chain_data.append({
                    'type': 'NARRATOR',
                    'narrator_id': item.narrator.id,
                    'narrator_name': item.narrator.name,
                    'method': item.method
                })

        return {
            'hadith_name': self.hadith_name,
            'matn': self.matn,
            'chain': chain_data,
            'layout_style': self.layout_style
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], narrator_dict: Dict[int, Narrator]) -> 'Chain':
        """Create chain from dictionary."""
        chain = cls(
            hadith_name=data.get('hadith_name', ''),
            matn=data.get('matn', ''),
            layout_style=data.get('layout_style', 0)
        )

        for item_data in data.get('chain', []):
            if item_data.get('type') == 'BRANCH':
                branch = []
                for n_data in item_data.get('branch', []):
                    narrator_id = n_data.get('narrator_id')
                    narrator = narrator_dict.get(narrator_id)
                    if narrator:
                        branch.append((narrator, n_data.get('method', 'عن')))
                chain.add_branch([branch])
            else:
                narrator_id = item_data.get('narrator_id')
                narrator = narrator_dict.get(narrator_id)
                if narrator:
                    chain.add_narrator(narrator, item_data.get('method', 'عن'))

        return chain