from uuid import UUID

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.academics.admin_scope import SchoolScopedAdminAPIView
from apps.core.responses import success_response

from .models import EvaluationComponent, EvaluationScheme
from .serializers import (
    EvaluationComponentSerializer,
    EvaluationComponentWriteSerializer,
    EvaluationSchemeSerializer,
    EvaluationSchemeWriteSerializer,
)


def evaluation_scheme_queryset():
    return EvaluationScheme.objects.select_related(
        'course_offering',
        'course_offering__academic_period',
        'course_offering__course',
    ).prefetch_related(
        'components',
    )


def evaluation_component_queryset():
    return EvaluationComponent.objects.select_related(
        'scheme',
        'scheme__course_offering',
        'scheme__course_offering__academic_period',
        'scheme__course_offering__course',
    )


class EvaluationSchemeListView(SchoolScopedAdminAPIView):
    serializer_class = EvaluationSchemeSerializer
    professional_school_lookup = 'course_offering__course__professional_school_id'

    def get(self, request: Request) -> Response:
        schemes = self.get_scoped_queryset(
            request,
            evaluation_scheme_queryset(),
        )

        return success_response(
            data={
                'evaluation_schemes': EvaluationSchemeSerializer(
                    schemes,
                    many=True,
                ).data,
            },
            request_id=request.request_id,
        )

    def post(self, request: Request) -> Response:
        serializer = EvaluationSchemeWriteSerializer(
            data=request.data,
            context=self.get_write_serializer_context(request),
        )
        serializer.is_valid(raise_exception=True)
        scheme = serializer.save()

        return success_response(
            data=EvaluationSchemeSerializer(scheme).data,
            request_id=request.request_id,
            status_code=status.HTTP_201_CREATED,
        )


class EvaluationComponentListView(SchoolScopedAdminAPIView):
    serializer_class = EvaluationComponentSerializer
    professional_school_lookup = (
        'scheme__course_offering__course__professional_school_id'
    )

    def get(self, request: Request) -> Response:
        components = self.get_scoped_queryset(
            request,
            evaluation_component_queryset(),
        )

        return success_response(
            data={
                'evaluation_components': EvaluationComponentSerializer(
                    components,
                    many=True,
                ).data,
            },
            request_id=request.request_id,
        )

    def post(self, request: Request) -> Response:
        serializer = EvaluationComponentWriteSerializer(
            data=request.data,
            context=self.get_write_serializer_context(request),
        )
        serializer.is_valid(raise_exception=True)
        component = serializer.save()

        return success_response(
            data=EvaluationComponentSerializer(component).data,
            request_id=request.request_id,
            status_code=status.HTTP_201_CREATED,
        )


class EvaluationComponentDetailView(SchoolScopedAdminAPIView):
    serializer_class = EvaluationComponentWriteSerializer
    professional_school_lookup = (
        'scheme__course_offering__course__professional_school_id'
    )

    def patch(
        self,
        request: Request,
        component_id: UUID,
    ) -> Response:
        component = get_object_or_404(
            self.get_scoped_queryset(
                request,
                evaluation_component_queryset(),
            ),
            public_id=component_id,
        )
        serializer = EvaluationComponentWriteSerializer(
            component,
            data=request.data,
            partial=True,
            context=self.get_write_serializer_context(request),
        )
        serializer.is_valid(raise_exception=True)
        updated_component = serializer.save()

        return success_response(
            data=EvaluationComponentSerializer(updated_component).data,
            request_id=request.request_id,
        )
