from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.request import Request
from rest_framework.throttling import (
    AnonRateThrottle,
    UserRateThrottle,
)

if TYPE_CHECKING:
    from rest_framework.views import APIView


class RouteScopedAnonRateThrottle(AnonRateThrottle):
    def get_cache_key(
        self,
        request: Request,
        view: APIView,
    ) -> str | None:
        cache_key = super().get_cache_key(
            request,
            view,
        )

        if cache_key is None:
            return None

        resolver_match = getattr(
            request,
            'resolver_match',
            None,
        )
        view_name = getattr(
            resolver_match,
            'view_name',
            None,
        )

        if view_name is None:
            view_name = view.__class__.__qualname__

        return f'{cache_key}:{view_name}'


class AnonymousBurstRateThrottle(
    RouteScopedAnonRateThrottle,
):
    scope = 'anonymous_burst'


class AnonymousSustainedRateThrottle(
    RouteScopedAnonRateThrottle,
):
    scope = 'anonymous_sustained'


class AuthenticatedUserRateThrottle(
    UserRateThrottle,
):
    def get_cache_key(
        self,
        request: Request,
        view: APIView,
    ) -> str | None:
        user = request.user

        if not user or not user.is_authenticated:
            return None

        return self.cache_format % {
            'scope': self.scope,
            'ident': str(user.public_id),
        }


class UserBurstRateThrottle(
    AuthenticatedUserRateThrottle,
):
    scope = 'user_burst'


class UserSustainedRateThrottle(
    AuthenticatedUserRateThrottle,
):
    scope = 'user_sustained'
