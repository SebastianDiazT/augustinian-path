from django.contrib.auth.models import Group
from django.db.models import Prefetch
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.pagination import StandardPageNumberPagination
from apps.core.responses import success_response

from .models import User
from .permissions import IsPlatformAdmin
from .serializers import (
    PlatformAdminAccessDataSerializer,
    PlatformAdminUserListDataSerializer,
    PlatformAdminUserSerializer,
)


class PlatformAdminAccessView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsPlatformAdmin,
    ]

    @extend_schema(
        summary='Comprobar acceso administrativo',
        tags=['Administración'],
        responses=PlatformAdminAccessDataSerializer,
    )
    def get(self, request: Request) -> Response:
        return success_response(
            data={
                'authorized': True,
            },
            request_id=request.request_id,
        )


class PlatformAdminUserListView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsPlatformAdmin,
    ]

    @extend_schema(
        summary='Listar usuarios de la plataforma',
        tags=['Administración'],
        parameters=[
            OpenApiParameter(
                name='page',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Número de página.',
            ),
            OpenApiParameter(
                name='page_size',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Cantidad de usuarios por página. Máximo: 100.'),
            ),
        ],
        responses=PlatformAdminUserListDataSerializer,
    )
    def get(self, request: Request) -> Response:
        users = User.objects.prefetch_related(
            Prefetch(
                'groups',
                queryset=Group.objects.order_by('name'),
            )
        ).order_by('email')

        paginator = StandardPageNumberPagination()
        page = paginator.paginate_queryset(
            users,
            request,
            view=self,
        )

        serializer = PlatformAdminUserSerializer(
            page,
            many=True,
        )

        return success_response(
            data={
                'users': serializer.data,
                'pagination': paginator.get_metadata(),
            },
            request_id=request.request_id,
        )
