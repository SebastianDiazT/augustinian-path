from collections.abc import Callable
from uuid import UUID, uuid4

from django.http import HttpRequest, HttpResponse


class RequestIDMiddleware:
    header_name = 'X-Request-ID'

    def __init__(
        self,
        get_response: Callable[[HttpRequest], HttpResponse],
    ) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request_id = self._get_request_id(request.headers.get(self.header_name))

        request.request_id = request_id

        response = self.get_response(request)
        response[self.header_name] = request_id

        return response

    @staticmethod
    def _get_request_id(value: str | None) -> str:
        if value is None:
            return str(uuid4())

        try:
            return str(UUID(value))
        except ValueError:
            return str(uuid4())
