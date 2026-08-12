import uuid

from .context import request_id_var

REQUEST_ID_HEADER = 'X-Request-Id'


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        incoming = request.META.get('HTTP_X_REQUEST_ID')
        request_id = incoming or str(uuid.uuid4())

        request.request_id = request_id
        token = request_id_var.set(request_id)
        try:
            response = self.get_response(request)
        finally:
            request_id_var.reset(token)

        response[REQUEST_ID_HEADER] = request_id
        return response
