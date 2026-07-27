from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework.
    Provides consistent error response envelope.
    """
    response = exception_handler(exc, context)

    if response is not None:
        customized_response = {
            "success": False,
            "status_code": response.status_code,
            "error": {
                "type": exc.__class__.__name__,
                "details": response.data
            }
        }
        response.data = customized_response
    else:
        logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
        response = Response(
            {
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": {
                    "type": "InternalServerError",
                    "details": "An unexpected server error occurred."
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
