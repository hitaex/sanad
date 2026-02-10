"""
Search controller for narrator search functionality.
"""

import rapidfuzz
from models.narrator import Narrator


class SearchController:
    """Controller for narrator search operations."""

    def __init__(self, narrators):
        self.narrators = narrators

    def search_narrators(self, query, search_type, limit):
        """Search narrators with relevance ranking."""
        query_stripped = query.strip()
        query_lower = query_stripped.lower()

        if not query_lower:
            return []

        if search_type == 1:  # Exact search
            scored = []
            for narrator in self.narrators:
                search_text = self._narrator_search_string(narrator).lower()
                if query_lower in search_text:
                    score = self._exact_relevance_score(narrator, query_lower)
                    scored.append((score, narrator))
            scored.sort(key=lambda x: (-x[0], x[1].name))
            return [n for _, n in scored[:limit]]
        else:  # Fuzzy search
            scored = []
            for n in self.narrators:
                s = self._fuzzy_relevance_score(query_stripped, n)
                if s >= 35:
                    scored.append((s, n))
            scored.sort(key=lambda x: (-x[0], x[1].name))
            return [n for _, n in scored[:limit]]

    def _narrator_search_string(self, narrator):
        """Build full searchable string."""
        parts = [narrator.name]
        parts.extend(narrator.basic_info.values())
        for j in narrator.jarh_tadil:
            parts.append(j.get('scholar', ''))
            parts.append(j.get('comment', ''))
        return ' '.join(str(p) for p in parts if p)

    def _narrator_search_fields(self, narrator):
        """Return search fields for relevance weighting."""
        bi = narrator.basic_info
        name = narrator.name or ''
        kunya = bi.get('الكنية', '') or ''
        nasab = bi.get('النسب', '') or ''
        tabaqa = bi.get('طبقة رواة التقريب', '') or ''
        other_parts = [bi.get('اللقب', ''), bi.get('الاسم', '')]
        for j in narrator.jarh_tadil:
            other_parts.append(j.get('comment', ''))
            other_parts.append(j.get('scholar', ''))
        other = ' '.join(str(p) for p in other_parts if p)
        return (name, kunya, nasab, tabaqa, other)

    def _exact_relevance_score(self, narrator, query_lower):
        """Score for exact substring match."""
        name, kunya, nasab, tabaqa, other = self._narrator_search_fields(narrator)
        name_l = name.lower()
        kunya_l = kunya.lower()
        nasab_l = nasab.lower()
        tabaqa_l = tabaqa.lower()
        other_l = other.lower()

        score = 0
        if query_lower in name_l:
            score += 100
            if name_l.startswith(query_lower) or name_l == query_lower:
                score += 30
        if query_lower in kunya_l:
            score += 75
            if kunya_l == query_lower or kunya_l.startswith(query_lower):
                score += 25
        if query_lower in nasab_l:
            score += 55
        if query_lower in tabaqa_l:
            score += 45
        if query_lower in other_l:
            score += 25
        return score

    def _fuzzy_relevance_score(self, query, narrator):
        """Weighted fuzzy score."""
        name, kunya, nasab, tabaqa, other = self._narrator_search_fields(narrator)
        if not name and not kunya and not other:
            return 0

        name_s = rapidfuzz.fuzz.partial_ratio(query, name) if name else 0
        kunya_s = rapidfuzz.fuzz.partial_ratio(query, kunya) if kunya else 0
        nasab_s = rapidfuzz.fuzz.partial_ratio(query, nasab) if nasab else 0
        tabaqa_s = rapidfuzz.fuzz.partial_ratio(query, tabaqa) if tabaqa else 0
        other_s = rapidfuzz.fuzz.partial_ratio(query, other) if other else 0

        total = (3.0 * name_s + 2.2 * kunya_s + 1.2 * nasab_s + 1.0 * tabaqa_s + 0.5 * other_s)
        total /= (3.0 + 2.2 + 1.2 + 1.0 + 0.5) if (name or kunya or nasab or tabaqa or other) else 1
        return total