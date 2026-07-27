import re
import logging

logger = logging.getLogger(__name__)


class RegexExtractionService:
    """
    Regex Engine to extract contract metadata:
    - Contract Parties
    - Effective & Expiration Dates
    - Contract Duration
    - Governing Law
    - Jurisdiction
    """

    GOVERNING_LAW_PATTERNS = [
        r'(?:governed\s+by\s+(?:and\s+construed\s+in\s+accordance\s+with\s+)?the\s+laws\s+of\s+)(the\s+State\s+of\s+[A-Z][a-z]+|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'(?:laws\s+of\s+)(the\s+State\s+of\s+[A-Z][a-z]+|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?:\s+shall\s+govern)',
        r'(?:subject\s+to\s+the\s+exclusive\s+jurisdiction\s+of\s+the\s+laws\s+of\s+)(State\s+of\s+[A-Z][a-z]+|[A-Z][a-z]+)',
    ]

    JURISDICTION_PATTERNS = [
        r'(?:courts\s+of\s+)(the\s+State\s+of\s+[A-Z][a-z]+|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?:\s+shall\s+have\s+exclusive\s+jurisdiction)',
        r'(?:exclusive\s+jurisdiction\s+in\s+)(the\s+courts\s+of\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*|State\s+of\s+[A-Z][a-z]+|[A-Z][a-z]+)',
        r'(?:venue\s+shall\s+be\s+in\s+)(?:the\s+courts\s+of\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
    ]

    PARTIES_PATTERNS = [
        r'(?:BY\s+AND\s+BETWEEN|by\s+and\s+between)\s+([A-Z][A-Za-z0-9\s,\.\(\)]+?)(?:\s+AND\s+|\s+and\s+|\,\s*AND\s*)([A-Z][A-Za-z0-9\s,\.\(\)]+?)(?:\s*\,\s*dated|\s*effective|\s*\(collectively|\s*\.)',
        r'([A-Z][A-Za-z0-9\s,\.\-]+?\s*(?:Inc\.|LLC|Corp\.|Corporation|Ltd\.|Limited))\s+(?:\("?[A-Z][a-z]+"?\))',
    ]

    DATE_PATTERNS = [
        r'(?:effective\s+as\s+of|dated\s+as\s+of|entered\s+into\s+on|made\s+this)\s+([A-Z][a-z]+\s+\d{1,2},\s*\d{4}|\d{1,2}(?:st|nd|rd|th)?\s+day\s+of\s+[A-Z][a-z]+,\s*\d{4}|\d{4}-\d{2}-\d{2})',
        r'(?:term\s+shall\s+expire\s+on|terminating\s+on|ending\s+on)\s+([A-Z][a-z]+\s+\d{1,2},\s*\d{4}|\d{4}-\d{2}-\d{2})',
    ]

    DURATION_PATTERNS = [
        r'(?:term\s+of\s+)(this\s+Agreement\s+shall\s+be\s+for\s+)?(\d+\s*(?:years?|months?|days?))',
        r'(?:period\s+of\s+)(\d+\s*(?:years?|months?|days?))',
        r'(?:for\s+a\s+duration\s+of\s+)(\d+\s*(?:years?|months?|days?))',
    ]

    @classmethod
    def extract_metadata(cls, text):
        governing_law = cls._find_pattern(text, cls.GOVERNING_LAW_PATTERNS) or "Not Explicitly Stated"
        jurisdiction = cls._find_pattern(text, cls.JURISDICTION_PATTERNS) or "Not Explicitly Stated"
        duration = cls._find_pattern(text, cls.DURATION_PATTERNS) or "Standard / Unspecified"

        dates = []
        for pat in cls.DATE_PATTERNS:
            matches = re.findall(pat, text, re.IGNORECASE)
            for m in matches:
                if isinstance(m, tuple):
                    dates.extend([item for item in m if item])
                else:
                    dates.append(m)

        effective_date = dates[0] if dates else "Not Specified"
        expiration_date = dates[1] if len(dates) > 1 else "Not Specified"

        # Contract Parties extraction
        parties = []
        for pat in cls.PARTIES_PATTERNS:
            matches = re.findall(pat, text)
            for m in matches:
                if isinstance(m, tuple):
                    for item in m:
                        clean = item.strip().strip(',()')
                        if len(clean) > 3 and clean not in parties:
                            parties.append(clean)
                elif isinstance(m, str):
                    clean = m.strip().strip(',()')
                    if len(clean) > 3 and clean not in parties:
                        parties.append(clean)

        return {
            'governing_law': governing_law.strip(),
            'jurisdiction': jurisdiction.strip(),
            'contract_duration': duration.strip(),
            'effective_date': effective_date,
            'expiration_date': expiration_date,
            'contract_parties': parties[:4],
            'dates': dates[:6]
        }

    @staticmethod
    def _find_pattern(text, patterns):
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                for g in reversed(groups):
                    if g:
                        return g
        return None
