from uuid import UUID

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsStudent
from apps.core.responses import success_response

from .admin_views import syllabus_queryset
from .models import Syllabus
from .serializers import SyllabusSerializer


class StudentSyllabusAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsStudent,
    ]


class SyllabusCatalogView(StudentSyllabusAPIView):
    serializer_class = SyllabusSerializer

    @extend_schema(
        operation_id='syllabus_list',
        responses=SyllabusSerializer(many=True),
    )
    def get(self, request: Request) -> Response:
        syllabi = syllabus_queryset().filter(
            status=Syllabus.Status.PUBLISHED,
        )
        course_offering = request.query_params.get('course_offering')

        if course_offering:
            try:
                offering_id = serializers.UUIDField().run_validation(
                    course_offering,
                )
            except serializers.ValidationError as error:
                raise serializers.ValidationError(
                    {
                        'course_offering': error.detail,
                    }
                ) from error

            syllabi = syllabi.filter(
                course_offering__public_id=offering_id,
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


class SyllabusDetailView(StudentSyllabusAPIView):
    serializer_class = SyllabusSerializer

    @extend_schema(
        operation_id='syllabus_retrieve',
        responses=SyllabusSerializer,
    )
    def get(
        self,
        request: Request,
        syllabus_id: UUID,
    ) -> Response:
        syllabus = get_object_or_404(
            syllabus_queryset().filter(
                status=Syllabus.Status.PUBLISHED,
            ),
            public_id=syllabus_id,
        )

        return success_response(
            data=SyllabusSerializer(syllabus).data,
            request_id=request.request_id,
        )
