import uuid

from .context import reset_request_id, set_request_id

REQUEST_ID_HEADER = 'X-Request-Id'
REQUEST_ID_META_KEY = 'HTTP_X_REQUEST_ID'


class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        incoming_id = request.headers.get(REQUEST_ID_HEADER)
        request_id = (
            incoming_id.strip() if incoming_id and incoming_id.strip() else str(uuid.uuid4())
        )

        request.request_id = request_id

        token = set_request_id(request_id)
        try:
            response = self.get_response(request)
        finally:
            reset_request_id(token)

        response[REQUEST_ID_HEADER] = request_id
        return response
