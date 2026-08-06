from uuid import UUID

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.academics.eligibility import (
    evaluate_course_eligibility,
    get_student_academic_progress,
)
from apps.academics.models import CourseOffering, CurriculumCourse
from apps.accounts.permissions import IsStudent
from apps.core.responses import success_response

from .models import CourseSection, ScheduleScenario
from .serializers import (
    AvailableSectionQuerySerializer,
    CourseEligibilityQuerySerializer,
    CourseEligibilitySerializer,
    CourseSectionSerializer,
    ScenarioSelectionSerializer,
    ScenarioSelectionWriteSerializer,
    ScheduleConflictSerializer,
    ScheduleScenarioSerializer,
    ScheduleScenarioWriteSerializer,
)
from .services import detect_schedule_conflicts


def scenario_queryset():
    return ScheduleScenario.objects.select_related(
        'academic_period',
        'curriculum_plan',
        'curriculum_plan__professional_school',
        'curriculum_plan__professional_school__faculty',
    ).prefetch_related(
        'selections__course_offering__course',
        'selections__theory_section__meetings',
        'selections__theory_section__course_offering__curriculum_courses',
        'selections__laboratory_section__meetings',
        'selections__laboratory_section__course_offering__curriculum_courses',
    )


def get_user_scenario(
    request: Request,
    scenario_id: UUID,
) -> ScheduleScenario:
    return get_object_or_404(
        scenario_queryset(),
        public_id=scenario_id,
        user=request.user,
    )


class StudentSchedulingAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsStudent,
    ]


class AvailableCourseSectionListView(StudentSchedulingAPIView):
    serializer_class = CourseSectionSerializer

    def get(self, request: Request) -> Response:
        query_serializer = AvailableSectionQuerySerializer(
            data=request.query_params,
        )
        query_serializer.is_valid(raise_exception=True)
        filters = query_serializer.validated_data
        sections = (
            CourseSection.objects.filter(
                is_active=True,
                course_offering__is_active=True,
                course_offering__academic_period__is_active=True,
            )
            .select_related(
                'course_offering',
                'course_offering__academic_period',
                'course_offering__course',
            )
            .prefetch_related(
                'meetings',
                'course_offering__curriculum_courses',
            )
        )

        if 'academic_period' in filters:
            sections = sections.filter(
                course_offering__academic_period__public_id=(
                    filters['academic_period']
                ),
            )

        if 'curriculum_plan' in filters:
            sections = sections.filter(
                course_offering__curriculum_courses__curriculum_plan__public_id=(
                    filters['curriculum_plan']
                ),
            )

        sections = sections.distinct()

        return success_response(
            data={
                'course_sections': CourseSectionSerializer(
                    sections,
                    many=True,
                ).data,
            },
            request_id=request.request_id,
        )


class CourseEligibilityListView(StudentSchedulingAPIView):
    serializer_class = CourseEligibilitySerializer

    def get(self, request: Request) -> Response:
        query_serializer = CourseEligibilityQuerySerializer(
            data=request.query_params,
        )
        query_serializer.is_valid(raise_exception=True)
        filters = query_serializer.validated_data
        curriculum_courses = CurriculumCourse.objects.filter(
            curriculum_plan__public_id=filters['curriculum_plan'],
        ).select_related(
            'course',
        ).prefetch_related(
            'prerequisites__course',
        )
        offerings = (
            CourseOffering.objects.filter(
                is_active=True,
                academic_period__is_active=True,
                academic_period__public_id=filters['academic_period'],
                curriculum_courses__curriculum_plan__public_id=(
                    filters['curriculum_plan']
                ),
            )
            .select_related(
                'course',
                'academic_period',
            )
            .prefetch_related(
                Prefetch(
                    'curriculum_courses',
                    queryset=curriculum_courses,
                    to_attr='requested_curriculum_courses',
                )
            )
            .distinct()
        )
        results = []
        progress = None

        for offering in offerings:
            for curriculum_course in offering.requested_curriculum_courses:
                if progress is None:
                    progress = get_student_academic_progress(
                        request.user,
                        curriculum_course,
                    )
                eligibility = evaluate_course_eligibility(
                    request.user,
                    curriculum_course,
                    progress=progress,
                )
                results.append(
                    {
                        'course_offering_id': str(offering.public_id),
                        'curriculum_course_id': str(
                            curriculum_course.public_id,
                        ),
                        'course_code': offering.course.code,
                        'course_name': offering.course.name,
                        **eligibility.as_dict(),
                    }
                )

        return success_response(
            data={
                'course_eligibility': results,
            },
            request_id=request.request_id,
        )


class ScheduleScenarioListView(StudentSchedulingAPIView):
    serializer_class = ScheduleScenarioSerializer

    @extend_schema(
        operation_id='scheduling_scenario_list',
        responses=ScheduleScenarioSerializer(many=True),
    )
    def get(self, request: Request) -> Response:
        scenarios = scenario_queryset().filter(
            user=request.user,
        )

        return success_response(
            data={
                'scenarios': ScheduleScenarioSerializer(
                    scenarios,
                    many=True,
                ).data,
            },
            request_id=request.request_id,
        )

    def post(self, request: Request) -> Response:
        serializer = ScheduleScenarioWriteSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        scenario = serializer.save()

        return success_response(
            data=ScheduleScenarioSerializer(scenario).data,
            request_id=request.request_id,
            status_code=status.HTTP_201_CREATED,
        )


class ScheduleScenarioDetailView(StudentSchedulingAPIView):
    serializer_class = ScheduleScenarioSerializer

    @extend_schema(
        operation_id='scheduling_scenario_retrieve',
        responses=ScheduleScenarioSerializer,
    )
    def get(
        self,
        request: Request,
        scenario_id: UUID,
    ) -> Response:
        scenario = get_user_scenario(request, scenario_id)

        return success_response(
            data=ScheduleScenarioSerializer(scenario).data,
            request_id=request.request_id,
        )

    def patch(
        self,
        request: Request,
        scenario_id: UUID,
    ) -> Response:
        scenario = get_user_scenario(request, scenario_id)
        serializer = ScheduleScenarioWriteSerializer(
            scenario,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        updated_scenario = serializer.save()

        return success_response(
            data=ScheduleScenarioSerializer(updated_scenario).data,
            request_id=request.request_id,
        )


class ScenarioSelectionListView(StudentSchedulingAPIView):
    serializer_class = ScenarioSelectionSerializer

    def get(
        self,
        request: Request,
        scenario_id: UUID,
    ) -> Response:
        scenario = get_user_scenario(request, scenario_id)

        return success_response(
            data={
                'selections': ScenarioSelectionSerializer(
                    scenario.selections.all(),
                    many=True,
                ).data,
            },
            request_id=request.request_id,
        )

    def post(
        self,
        request: Request,
        scenario_id: UUID,
    ) -> Response:
        scenario = get_user_scenario(request, scenario_id)
        serializer = ScenarioSelectionWriteSerializer(
            data=request.data,
            context={
                'scenario': scenario,
            },
        )
        serializer.is_valid(raise_exception=True)
        selection = serializer.save()

        return success_response(
            data=ScenarioSelectionSerializer(selection).data,
            request_id=request.request_id,
            status_code=status.HTTP_201_CREATED,
        )


class ScenarioSelectionDetailView(StudentSchedulingAPIView):
    serializer_class = ScenarioSelectionWriteSerializer

    def patch(
        self,
        request: Request,
        scenario_id: UUID,
        selection_id: UUID,
    ) -> Response:
        scenario = get_user_scenario(request, scenario_id)
        selection = get_object_or_404(
            scenario.selections.all(),
            public_id=selection_id,
        )
        serializer = ScenarioSelectionWriteSerializer(
            selection,
            data=request.data,
            partial=True,
            context={
                'scenario': scenario,
            },
        )
        serializer.is_valid(raise_exception=True)
        updated_selection = serializer.save()

        return success_response(
            data=ScenarioSelectionSerializer(updated_selection).data,
            request_id=request.request_id,
        )

    def delete(
        self,
        request: Request,
        scenario_id: UUID,
        selection_id: UUID,
    ) -> Response:
        scenario = get_user_scenario(request, scenario_id)
        selection = get_object_or_404(
            scenario.selections.all(),
            public_id=selection_id,
        )
        selection.delete()

        return success_response(
            data=None,
            request_id=request.request_id,
            status_code=status.HTTP_204_NO_CONTENT,
        )


class ScheduleConflictListView(StudentSchedulingAPIView):
    serializer_class = ScheduleConflictSerializer

    def get(
        self,
        request: Request,
        scenario_id: UUID,
    ) -> Response:
        scenario = get_user_scenario(request, scenario_id)
        conflicts = [
            conflict.as_dict()
            for conflict in detect_schedule_conflicts(
                scenario,
            )
        ]

        return success_response(
            data={
                'conflicts': conflicts,
                'has_conflicts': bool(conflicts),
            },
            request_id=request.request_id,
        )
