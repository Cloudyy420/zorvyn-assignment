from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        # Unhandled exceptions (not raised by DRF)
        return Response({
            'status': 'error',
            'message': 'An unexpected error occurred',
            'details': str(exc)
        }, status=500)

    error_detail = response.data
    if isinstance(error_detail, dict):
        messages = []
        for field, errors in error_detail.items():
            if isinstance(errors, (list, dict)):
                for err in errors if isinstance(errors, list) else [errors]:
                    messages.append(f"{field}: {err}")
            else:
                messages.append(f"{field}: {errors}")
        message_text = "; ".join(messages)
    else:
        message_text = str(error_detail)

    response.data = {
        'status': 'error',
        'message': message_text,
        'details': error_detail
    }

    return response