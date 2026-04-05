"""
Consistent response formatters for the API.
Provides standard response structures and status codes.
"""
from rest_framework import status
from rest_framework.response import Response


class APIResponse:
    """Standard API response formatter."""

    @staticmethod
    def success(data=None, message="Success", status_code=status.HTTP_200_OK):
        """Success response."""
        return Response(
            {
                "success": True,
                "message": message,
                "data": data,
            },
            status=status_code,
        )

    @staticmethod
    def created(data, message="Resource created successfully"):
        """Resource created response (201)."""
        return Response(
            {
                "success": True,
                "message": message,
                "data": data,
            },
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def deleted(message="Resource deleted successfully"):
        """Resource deleted response (204)."""
        return Response(
            {
                "success": True,
                "message": message,
            },
            status=status.HTTP_204_NO_CONTENT,
        )

    @staticmethod
    def error(message, error_code=None, status_code=status.HTTP_400_BAD_REQUEST, details=None):
        """Error response."""
        response_data = {
            "success": False,
            "message": message,
        }
        if error_code:
            response_data["error_code"] = error_code
        if details:
            response_data["details"] = details
        return Response(response_data, status=status_code)

    @staticmethod
    def validation_error(message, details, status_code=status.HTTP_400_BAD_REQUEST):
        """Validation error response."""
        return APIResponse.error(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status_code,
            details=details,
        )

    @staticmethod
    def unauthorized(message="Unauthorized access"):
        """Unauthorized response (401)."""
        return APIResponse.error(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    @staticmethod
    def forbidden(message="Access denied"):
        """Forbidden response (403)."""
        return APIResponse.error(
            message=message,
            error_code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    @staticmethod
    def not_found(message="Resource not found"):
        """Not found response (404)."""
        return APIResponse.error(
            message=message,
            error_code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    @staticmethod
    def conflict(message, details=None):
        """Conflict response (409) - e.g., duplicate resource."""
        return APIResponse.error(
            message=message,
            error_code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )
