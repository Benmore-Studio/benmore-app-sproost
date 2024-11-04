# utils.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Custom exception handler that modifies the response for authentication errors.
    """
    # Let DRF handle the default exceptions first
    response = exception_handler(exc, context)

    # Customize the response for 401 Unauthorized
    if response is not None and response.status_code == status.HTTP_401_UNAUTHORIZED:
        custom_response_data = {
            'error': 'You are not authorized. Please provide valid credentials.'
        }
        return Response(custom_response_data, status=status.HTTP_401_UNAUTHORIZED)

    # Return the original response if it's not a 401 Unauthorized error
    return response
