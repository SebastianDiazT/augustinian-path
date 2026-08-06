from uuid import UUID

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.academics.admin_scope import SchoolScopedAdminAPIView
from apps.core.responses import success_response

from .models import Syllabus
from .serializers import SyllabusSerializer, SyllabusWriteSerializer


def syllabus_queryset():
    return Syllabus.objects.select_related(
        'course_offering',
        'course_offering__academic_period',
        'course_offering__course',
        'course_offering__course__professional_school',
        'curriculum_course',
        'curriculum_course__curriculum_plan',
    ).prefetch_related(
        'curriculum_course__prerequisites__course',
        'course_offering__evaluation_scheme__components',
    )


class SyllabusListView(SchoolScopedAdminAPIView):
    serializer_class = SyllabusSerializer
    professional_school_lookup = (
        'course_offering__course__professional_school_id'
    )

    @extend_schema(
        operation_id='admin_syllabus_list',
        responses=SyllabusSerializer(many=True),
    )
    def get(self, request: Request) -> Response:
        syllabi = self.get_scoped_queryset(
            request,
            syllabus_queryset(),
        )

        return success_response(
            data={
                'syllabi': SyllabusSerializer(
                    syllabi,
                    many=True,
                ).data,
            },
            request_id=request.request_id,
        )

    @extend_schema(
        operation_id='admin_syllabus_create',
        request=SyllabusWriteSerializer,
        responses=SyllabusSerializer,
    )
    def post(self, request: Request) -> Response:
        serializer = SyllabusWriteSerializer(
            data=request.data,
            context=self.get_write_serializer_context(request),
        )
        serializer.is_valid(raise_exception=True)
        syllabus = serializer.save()

        return success_response(
            data=SyllabusSerializer(
                syllabus_queryset().get(pk=syllabus.pk),
            ).data,
            request_id=request.request_id,
            status_code=status.HTTP_201_CREATED,
        )


class SyllabusDetailView(SchoolScopedAdminAPIView):
    serializer_class = SyllabusWriteSerializer
    professional_school_lookup = (
        'course_offering__course__professional_school_id'
    )

    @extend_schema(
        operation_id='admin_syllabus_retrieve',
        responses=SyllabusSerializer,
    )
    def get(
        self,
        request: Request,
        syllabus_id: UUID,
    ) -> Response:
        syllabus = self._get_syllabus(request, syllabus_id)

        return success_response(
            data=SyllabusSerializer(syllabus).data,
            request_id=request.request_id,
        )

    @extend_schema(
        operation_id='admin_syllabus_update',
        request=SyllabusWriteSerializer,
        responses=SyllabusSerializer,
    )
    def patch(
        self,
        request: Request,
        syllabus_id: UUID,
    ) -> Response:
        syllabus = self._get_syllabus(request, syllabus_id)
        serializer = SyllabusWriteSerializer(
            syllabus,
            data=request.data,
            partial=True,
            context=self.get_write_serializer_context(request),
        )
        serializer.is_valid(raise_exception=True)
        updated_syllabus = serializer.save()

        return success_response(
            data=SyllabusSerializer(
                syllabus_queryset().get(pk=updated_syllabus.pk),
            ).data,
            request_id=request.request_id,
        )

    def _get_syllabus(
        self,
        request: Request,
        syllabus_id: UUID,
    ) -> Syllabus:
        return get_object_or_404(
            self.get_scoped_queryset(
                request,
                syllabus_queryset(),
            ),
            public_id=syllabus_id,
        )
