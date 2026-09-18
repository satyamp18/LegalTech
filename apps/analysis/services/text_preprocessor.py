import re
from typing import List, Dict


class TextPreprocessingService:
    """
    Text Normalization & Preprocessing Service.
    Cleans raw PDF text extractions, strips unnecessary whitespace/control characters,
    and splits document into logical sections.
    """

    @staticmethod
    def clean_text(raw_text: str) -> str:
        """
        Normalizes raw contract text by removing excessive blank lines,
        tabs, and non-standard control characters.
        """
        if not raw_text:
            return ""

        # Normalize line endings
        text = raw_text.replace('\r\n', '\n').replace('\r', '\n')
        # Remove non-printable control characters except newline & tab
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        # Collapse multi-blank lines down to double newline
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Strip trailing whitespace on each line
        lines = [line.strip() for line in text.split('\n')]
        
        return '\n'.join(lines).strip()

    @staticmethod
    def extract_sections(text: str) -> List[Dict[str, str]]:
        """
        Splits text into logical sections based on headers like '1. DEFINITIONS', 'ARTICLE 2', etc.
        Uses basic regex matching and list indexing.
        """
        cleaned = TextPreprocessingService.clean_text(text)
        if not cleaned:
            return []

        # Match common section headers (e.g. "Section 1.", "ARTICLE I", "1. TERMINATION")
        section_pattern = r'(?:\n|^)(?:SECTION|ARTICLE|\d+\.)\s*([A-Z0-9\.\s]{3,50})(?=\n)'
        matches = list(re.finditer(section_pattern, cleaned, re.IGNORECASE))

        sections = []
        if not matches:
            # Fallback: single section if no formal section headers found
            sections.append({
                "title": "Full Document Content",
                "content": cleaned
            })
            return sections

        for i, match in enumerate(matches):
            title = match.group(0).strip()
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned)
            content = cleaned[start_pos:end_pos].strip()

            if content:
                sections.append({
                    "title": title,
                    "content": content
                })

        return sections
