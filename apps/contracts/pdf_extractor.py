import os
import re
# pyrefly: ignore [missing-import]
import fitz
import logging

logger = logging.getLogger(__name__)


class PDFExtractorService:
    """
    Service for extracting clean and structured text from PDF documents using PyMuPDF.
    """

    def extract_text(self, file_path: str) -> str:
        """
        Extracts and cleans text page-by-page from a PDF file located at file_path.
        Raises FileNotFoundError if the file is missing.
        Raises ValueError if the PDF is corrupt or unreadable.
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found at: {file_path}")
            raise FileNotFoundError(f"PDF file not found at: {file_path}")

        doc = None
        try:
            doc = fitz.open(file_path)
        except Exception as e:
            logger.exception(f"Failed to open PDF file at {file_path}")
            raise ValueError("Corrupted or invalid PDF file structure. PyMuPDF could not parse the document.") from e

        try:
            full_text_pages = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # 'blocks' mode extracts coordinates and text separated into logical block groupings
                blocks = page.get_text("blocks")
                
                # Sort blocks top-to-bottom (y-coordinate) then left-to-right (x-coordinate)
                blocks.sort(key=lambda b: (b[1], b[0]))
                
                page_text_blocks = []
                for block in blocks:
                    # Skip non-text blocks (block[6] is block_type: 0 for text, 1 for image)
                    if len(block) >= 7 and block[6] != 0:
                        continue
                    
                    block_text = block[4].strip()
                    if not block_text:
                        continue
                    
                    cleaned_block = self._clean_block_text(block_text)
                    if cleaned_block:
                        page_text_blocks.append(cleaned_block)
                
                # Join this page's blocks with double newlines
                if page_text_blocks:
                    full_text_pages.append("\n\n".join(page_text_blocks))
            
            # Join pages together using a standardized PAGE BREAK token
            return "\n\n--- PAGE BREAK ---\n\n".join(full_text_pages) if full_text_pages else ""

        except Exception as e:
            logger.exception(f"Error occurred while parsing pages in {file_path}")
            raise ValueError("Failed to extract text from PDF due to an internal parsing error.") from e
        finally:
            if doc:
                doc.close()
                logger.info(f"Closed PDF document handle for {file_path}")

    def _clean_block_text(self, text: str) -> str:
        """
        Cleans a block of text:
        - Replaces tabs and consecutive spaces with a single space.
        - Merges soft-wrapped lines, keeping headings and hard sentence endings on distinct lines.
        """
        # Compress white spaces
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Split block into distinct lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return ""

        merged_lines = []
        current_line = lines[0]

        for next_line in lines[1:]:
            # If the current line ends in a hyphen (indicates word splitting), merge without space
            if current_line.endswith('-'):
                current_line = current_line[:-1] + next_line
            # If current line ends in standard sentence punctuation, keep them split
            elif current_line[-1] in ('.', ':', '!', '?'):
                merged_lines.append(current_line)
                current_line = next_line
            # If current line or next line is a likely heading, keep them split
            elif self._is_likely_heading(current_line) or self._is_likely_heading(next_line):
                merged_lines.append(current_line)
                current_line = next_line
            else:
                # Merge current line and next line with a single space
                current_line = current_line + " " + next_line

        merged_lines.append(current_line)
        return "\n".join(merged_lines)

    def _is_likely_heading(self, line: str) -> bool:
        """
        Checks if a line looks like a title or section heading:
        - Completely uppercase
        - Starts with common numbering formats (e.g. 1.1, Article II, Section 4)
        """
        line = line.strip()
        if not line:
            return False
            
        # Condition 1: All capitalized letters and not excessively long
        if line.isupper() and len(line) < 80:
            return True
            
        # Condition 2: Section or clause numbering patterns
        section_numbering_pattern = r'^(\d+(\.\d+)*|Section\s+\d+|Article\s+[IVXLCDM]+)\b'
        if re.match(section_numbering_pattern, line, re.IGNORECASE):
            return True
            
        return False
