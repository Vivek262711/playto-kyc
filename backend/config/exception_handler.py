"""
Custom DRF exception handler.
Ensures ALL API errors return: {"error": "message"}
"""
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # Flatten DRF's default error structure into {"error": "message"}
        detail = response.data

        if isinstance(detail, dict):
            if 'detail' in detail:
                message = str(detail['detail'])
            elif 'error' in detail:
                message = str(detail['error'])
            else:
                # Collect field errors into a single string
                messages = []
                for field, errors in detail.items():
                    if isinstance(errors, list):
                        for err in errors:
                            messages.append(f"{field}: {err}")
                    else:
                        messages.append(f"{field}: {errors}")
                message = '; '.join(messages)
        elif isinstance(detail, list):
            message = '; '.join(str(item) for item in detail)
        else:
            message = str(detail)

        response.data = {'error': message}

    return response
