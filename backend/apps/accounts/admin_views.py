from uuid import UUID

from django.contrib.auth.models import Group
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.academics.models import ProfessionalSchool
from apps.core.openapi import success_response_schema
from apps.core.pagination import StandardPageNumberPagination
from apps.core.responses import success_response
from apps.core.serializers import ApiErrorResponseSerializer

from .filters import PlatformAdminUserFilter
from .models import User
from .permissions import IsPlatformAdmin
from .roles import Role
from .serializers import (
    AcademicAdminAssignmentWriteSerializer,
    PlatformAdminAccessDataSerializer,
    PlatformAdminUserListDataSerializer,
    PlatformAdminUserSerializer,
)
from .services import (
    assign_academic_admin,
    remove_academic_admin,
)


class PlatformAdminAccessView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsPlatformAdmin,
    ]

    @extend_schema(
        summary='Comprobar acceso administrativo',
        tags=['Administración'],
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name='PlatformAdminAccessSuccessResponse',
                data_serializer=PlatformAdminAccessDataSerializer,
            ),
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
        },
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
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name='PlatformAdminUserListSuccessResponse',
                data_serializer=PlatformAdminUserListDataSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: ApiErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: ApiErrorResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        users = (
            User.objects.select_related(
                'academic_admin_assignment__professional_school',
            )
            .prefetch_related(
                Prefetch(
                    'groups',
                    queryset=Group.objects.order_by('name'),
                    to_attr='ordered_roles',
                )
            )
            .order_by('email')
        )

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


class PlatformAdminAcademicAdminAssignmentView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsPlatformAdmin,
    ]

    @extend_schema(
        summary='Asignar una escuela a un administrador académico',
        tags=['Administración'],
        request=AcademicAdminAssignmentWriteSerializer,
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name=('PlatformAdminAcademicAdminAssignmentSuccessResponse'),
                data_serializer=PlatformAdminUserSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: ApiErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: ApiErrorResponseSerializer,
        },
    )
    def put(
        self,
        request: Request,
        user_id: UUID,
    ) -> Response:
        input_serializer = AcademicAdminAssignmentWriteSerializer(
            data=request.data,
        )
        input_serializer.is_valid(
            raise_exception=True,
        )

        target_user = get_object_or_404(
            User,
            public_id=user_id,
        )

        if not target_user.is_active:
            raise ValidationError(
                {
                    'user_id': [
                        (
                            'No se puede asignar administración '
                            'académica a un usuario inactivo.'
                        ),
                    ],
                }
            )

        professional_school = get_object_or_404(
            ProfessionalSchool,
            public_id=input_serializer.validated_data['professional_school_id'],
            is_active=True,
        )

        updated_user = assign_academic_admin(
            user=target_user,
            professional_school=professional_school,
        )

        output_serializer = PlatformAdminUserSerializer(
            updated_user,
        )

        return success_response(
            data=output_serializer.data,
            request_id=request.request_id,
        )

    @extend_schema(
        summary='Retirar la administración académica de un usuario',
        tags=['Administración'],
        request=None,
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name=('PlatformAdminAcademicAdminRemovalSuccessResponse'),
                data_serializer=PlatformAdminUserSerializer,
            ),
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: ApiErrorResponseSerializer,
        },
    )
    def delete(
        self,
        request: Request,
        user_id: UUID,
    ) -> Response:
        target_user = get_object_or_404(
            User,
            public_id=user_id,
        )

        updated_user = remove_academic_admin(
            user=target_user,
        )

        output_serializer = PlatformAdminUserSerializer(
            updated_user,
        )

        return success_response(
            data=output_serializer.data,
            request_id=request.request_id,
        )
