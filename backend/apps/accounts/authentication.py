from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request


class BearerChallengeAuthentication(BaseAuthentication):
    """Proporciona el challenge Bearer sin autenticar el request."""

    def authenticate(
        self,
        _request: Request,
    ) -> None:
        return None

    def authenticate_header(
        self,
        _request: Request,
    ) -> str:
        return 'Bearer realm="api"'
