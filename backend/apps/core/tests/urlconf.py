"""
Urlconf usado solo por los tests (vía `@pytest.mark.urls`) para poder
simular cada tipo de error sin necesitar un endpoint de negocio real.
"""

from django.urls import path
from rest_framework.exceptions import (
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.error_views import custom_404_view, custom_500_view
from apps.core.pagination import EnvelopePageNumberPagination

# Mismos handlers que en config/urls.py, para que el 404/500 a nivel Django
# (URL sin match, o excepción en una vista que no es de DRF) también se
# pueda probar usando este urlconf.
handler404 = custom_404_view
handler500 = custom_500_view


class _OpenAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []


class RaiseValidationErrorView(_OpenAPIView):
    def get(self, request):
        raise ValidationError({'nombre': ['Este campo es requerido']})


class RaiseNotFoundView(_OpenAPIView):
    def get(self, request):
        raise NotFound()


class RaisePermissionDeniedView(_OpenAPIView):
    def get(self, request):
        raise PermissionDenied()


class RaiseNotAuthenticatedView(_OpenAPIView):
    def get(self, request):
        raise NotAuthenticated()


class RaiseUnhandledView(_OpenAPIView):
    def get(self, request):
        raise RuntimeError('boom - detalle interno que nunca debe salir en la respuesta')


class DetailView(_OpenAPIView):
    def get(self, request):
        return Response({'id': 1, 'nombre': 'Test'})


class PaginatedListView(_OpenAPIView):
    pagination_class = EnvelopePageNumberPagination

    def get(self, request):
        items = [{'n': i} for i in range(1, 98)]  # 97 items
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(items, request, view=self)
        return paginator.get_paginated_response(page)


def plain_django_view_that_raises(request):
    raise RuntimeError('boom fuera del ciclo de DRF')


urlpatterns = [
    path('validation-error/', RaiseValidationErrorView.as_view()),
    path('not-found/', RaiseNotFoundView.as_view()),
    path('permission-denied/', RaisePermissionDeniedView.as_view()),
    path('not-authenticated/', RaiseNotAuthenticatedView.as_view()),
    path('unhandled/', RaiseUnhandledView.as_view()),
    path('detail/', DetailView.as_view()),
    path('paginated/', PaginatedListView.as_view()),
    path('plain-500/', plain_django_view_that_raises),
]
