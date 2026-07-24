from rest_framework import status, parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from apps.contracts.serializers import DocumentUploadSerializer
import logging

logger = logging.getLogger(__name__)


class DocumentUploadView(APIView):
    """
    API endpoint to securely upload a PDF contract, validate its integrity/size,
    save it to the media directory, and record its metadata in the database.
    """
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    @extend_schema(
        operation_id="upload_document",
        description="Securely uploads a PDF contract, validates its format, size, signature, and records metadata.",
        request=DocumentUploadSerializer,
        responses={
            201: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        }
    )
    def post(self, request, *args, **kwargs):
        logger.info("Received request to upload a contract document.")
        serializer = DocumentUploadSerializer(data=request.data, context={'request': request})
        
        try:
            if serializer.is_valid():
                document = serializer.save()
                
                # Process text extraction synchronously using the DocumentService
                from apps.contracts.services import DocumentService
                doc_service = DocumentService()
                try:
                    doc_service.process_document_text_extraction(document)
                except Exception as parse_error:
                    logger.error(f"Text extraction failed during upload for document {document.id}: {str(parse_error)}")
                
                 # Refresh model instance from DB to get the latest status
                document.refresh_from_db()

                # Process Named Entity Recognition (NER) on the extracted text
                from apps.parser.entity_extractor import EntityExtractionService
                entity_service = EntityExtractionService()
                entities = {
                    "organizations": [],
                    "dates": [],
                    "locations": [],
                    "persons": []
                }
                
                if document.extracted_text:
                    try:
                        entities = entity_service.extract_entities(document.extracted_text)
                    except Exception as ner_error:
                        logger.error(f"NER extraction failed during upload for document {document.id}: {str(ner_error)}")
                
                # Extract filename basename
                filename = document.uploaded_file.name.split('/')[-1].split('\\')[-1]
                
                response_data = {
                    "document_id": str(document.id),
                    "filename": filename,
                    "upload_status": document.status,
                    "upload status": document.status,
                    "upload_timestamp": document.upload_date.isoformat(),
                    "upload timestamp": document.upload_date.isoformat(),
                    "entities": entities,
                }
                
                logger.info(f"Successfully processed upload and extraction for document {document.id} (Status: {document.status})")
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            logger.warning(f"Validation failed for document upload: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.exception("An unexpected error occurred during document upload.")
            return Response(
                {"error": "An unexpected error occurred during processing. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
