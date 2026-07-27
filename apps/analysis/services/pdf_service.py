import fitz  # PyMuPDF
import logging

logger = logging.getLogger(__name__)


class PDFProcessingService:
    """
    Extracts text, metadata, page count, and layout blocks using PyMuPDF (fitz).
    """

    @staticmethod
    def extract_pdf_data(file_path):
        """
        Parses a PDF file and returns structured data:
        - raw_text: Entire document text string
        - page_count: Total pages
        - pages: List of dicts containing page_number, text, and blocks
        """
        try:
            doc = fitz.open(file_path)
            page_count = len(doc)
            pages = []
            full_text_list = []

            for page_num in range(page_count):
                page = doc.load_page(page_num)
                page_text = page.get_text("text")
                blocks = page.get_text("blocks")  # Extract block layout (x0, y0, x1, y1, text, block_no, block_type)

                clean_blocks = []
                for b in blocks:
                    if len(b) >= 5 and isinstance(b[4], str):
                        clean_blocks.append({
                            'text': b[4].strip(),
                            'bbox': [b[0], b[1], b[2], b[3]]
                        })

                pages.append({
                    'page_number': page_num + 1,
                    'text': page_text,
                    'blocks': clean_blocks
                })
                full_text_list.append(page_text)

            doc.close()
            raw_text = "\n\n".join(full_text_list)

            return {
                'raw_text': raw_text,
                'page_count': page_count,
                'pages': pages
            }

        except Exception as e:
            logger.error(f"Error parsing PDF file with PyMuPDF: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to process PDF document: {str(e)}")
