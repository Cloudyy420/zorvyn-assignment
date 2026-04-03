from rest_framework.exceptions import APIException


class InvalidInputException(APIException):
    status_code = 400
    default_detail = 'Invalid input provided.'


class ValidationException(APIException):
    status_code = 400
    default_detail = 'Validation failed. Please check your input.'


class NotAuthenticatedException(APIException):
    status_code = 401
    default_detail = 'You are not authenticated. Please login first.'


class UnauthorizedAccessException(APIException):
    status_code = 403
    default_detail = 'You do not have permission to access this resource.'


class ResourceNotFoundException(APIException):
    status_code = 404
    default_detail = 'The requested resource was not found.'


class MethodNotAllowedException(APIException):
    status_code = 405
    default_detail = 'Method not allowed for this request.'


class DuplicateResourceException(APIException):
    status_code = 409
    default_detail = 'Resource already exists.'


class UnsupportedMediaTypeException(APIException):
    status_code = 415
    default_detail = 'Unsupported media type for this request.'


class ThrottledException(APIException):
    status_code = 429
    default_detail = 'Too many requests. Please try again later.'


class InternalServerErrorException(APIException):
    status_code = 500
    default_detail = 'Internal server error. Please try again later.'


class ServiceUnavailableException(APIException):
    status_code = 503
    default_detail = 'Service is temporarily unavailable.'


class TimeoutException(APIException):
    status_code = 504
    default_detail = 'Gateway timeout. Please try again later.'

class InvalidAmountException(APIException):
    status_code = 504
    default_detail = 'Amount is not valid. Please try again later.'
