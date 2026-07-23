import os
import logging
from apps.contracts.models import Document
from apps.contracts.pdf_extractor import PDFExtractorService

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Service layer to coordinate document processing workflows.
    """

    def __init__(self, extractor_service: PDFExtractorService = None):
        self.extractor_service = extractor_service or PDFExtractorService()

    def process_document_text_extraction(self, document: Document) -> str:
        """
        Coordinates text extraction from an uploaded Document's PDF file.
        Updates document status throughout the cycle and saves the extracted text to the DB.
        """
        # Ensure file exists on disk
        if not document.uploaded_file or not os.path.exists(document.uploaded_file.path):
            error_msg = f"Document file not found on disk for document ID {document.id} at path {getattr(document.uploaded_file, 'path', 'None')}"
            logger.error(error_msg)
            document.status = Document.DocumentStatus.FAILED
            document.save()
            raise FileNotFoundError(error_msg)

        logger.info(f"Starting text extraction for Document ID {document.id} (Title: '{document.title}')")
        
        # Transition to processing state
        document.status = Document.DocumentStatus.PROCESSING
        document.save()

        try:
            # Extract cleaned text
            extracted_text = self.extractor_service.extract_text(document.uploaded_file.path)
            
            # Save results and transition to parsed state
            document.extracted_text = extracted_text
            document.status = Document.DocumentStatus.PARSED
            document.save()

            logger.info(f"Successfully processed Document ID {document.id}. Extracted {len(extracted_text)} characters.")
            return extracted_text

        except Exception as e:
            logger.error(f"Text extraction failed for Document ID {document.id}: {str(e)}", exc_info=True)
            # Transition to failed state
            document.status = Document.DocumentStatus.FAILED
            document.save()
            raise
