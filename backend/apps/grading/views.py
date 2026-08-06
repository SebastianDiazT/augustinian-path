from uuid import UUID

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsStudent
from apps.core.responses import success_response

from .models import EvaluationScheme
from .serializers import (
    EvaluationSchemeSerializer,
    GradeSimulationRequestSerializer,
)
from .services import GradeSimulationError, simulate_grades


def student_scheme_queryset():
    return EvaluationScheme.objects.filter(
        course_offering__is_active=True,
        course_offering__academic_period__is_active=True,
    ).select_related(
        'course_offering',
        'course_offering__academic_period',
        'course_offering__course',
    ).prefetch_related(
        'components',
    )


class StudentGradingAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsStudent,
    ]


class EvaluationSchemeCatalogView(StudentGradingAPIView):
    serializer_class = EvaluationSchemeSerializer

    def get(self, request: Request) -> Response:
        schemes = student_scheme_queryset()
        course_offering = request.query_params.get('course_offering')

        if course_offering:
            query_serializer = serializers.UUIDField()

            try:
                offering_id = query_serializer.run_validation(course_offering)
            except serializers.ValidationError as error:
                raise serializers.ValidationError(
                    {
                        'course_offering': error.detail,
                    }
                ) from error

            schemes = schemes.filter(
                course_offering__public_id=offering_id,
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


class GradeSimulationView(StudentGradingAPIView):
    serializer_class = GradeSimulationRequestSerializer

    def post(
        self,
        request: Request,
        scheme_id: UUID,
    ) -> Response:
        scheme = get_object_or_404(
            student_scheme_queryset(),
            public_id=scheme_id,
        )
        serializer = GradeSimulationRequestSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        grades = serializer.validated_data['grades']
        public_ids = [grade['component_id'] for grade in grades]
        components = {
            component.public_id: component
            for component in scheme.components.filter(
                public_id__in=public_ids,
            )
        }

        if len(components) != len(public_ids):
            raise serializers.ValidationError(
                {
                    'grades': (
                        'Todas las notas deben pertenecer al esquema seleccionado.'
                    ),
                }
            )

        scores = {
            components[grade['component_id']].pk: grade['score']
            for grade in grades
        }

        try:
            result = simulate_grades(
                scheme,
                scores,
            )
        except GradeSimulationError as error:
            raise serializers.ValidationError(
                {
                    'grades': str(error),
                }
            ) from error

        return success_response(
            data=result,
            request_id=request.request_id,
        )
