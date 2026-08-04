from django.contrib.auth.models import Group
from django.db.models import Prefetch
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.openapi import success_response_schema
from apps.core.pagination import StandardPageNumberPagination
from apps.core.responses import success_response

from .filters import PlatformAdminUserFilter
from .models import User
from .permissions import IsPlatformAdmin
from .roles import Role
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
        responses=success_response_schema(
            component_name='PlatformAdminAccessSuccessResponse',
            data_serializer=PlatformAdminAccessDataSerializer,
        ),
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
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Busca parcialmente por correo, nombres o apellidos.'),
            ),
            OpenApiParameter(
                name='role',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                enum=[role.value for role in Role],
                description='Filtra por rol.',
            ),
            OpenApiParameter(
                name='is_active',
                type=bool,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtra por estado activo.',
            ),
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
        responses=success_response_schema(
            component_name='PlatformAdminUserListSuccessResponse',
            data_serializer=PlatformAdminUserListDataSerializer,
        ),
    )
    def get(self, request: Request) -> Response:
        users = User.objects.prefetch_related(
            Prefetch(
                'groups',
                queryset=Group.objects.order_by('name'),
            )
        ).order_by('email')

        user_filter = PlatformAdminUserFilter(
            data=request.query_params,
            queryset=users,
        )

        if not user_filter.is_valid():
            raise ValidationError(user_filter.errors)

        filtered_users = user_filter.qs

        paginator = StandardPageNumberPagination()
        page = paginator.paginate_queryset(
            filtered_users,
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
