from uuid import UUID

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.academics.admin_scope import SchoolScopedAdminAPIView
from apps.core.responses import success_response

from .models import ClassMeeting, CourseSection
from .serializers import (
    ClassMeetingSerializer,
    ClassMeetingWriteSerializer,
    CourseSectionSerializer,
    CourseSectionWriteSerializer,
)


def course_section_queryset():
    return CourseSection.objects.select_related(
        'course_offering',
        'course_offering__academic_period',
        'course_offering__course',
    ).prefetch_related(
        'meetings',
        'course_offering__curriculum_courses',
    )


def class_meeting_queryset():
    return ClassMeeting.objects.select_related(
        'section',
        'section__course_offering',
        'section__course_offering__academic_period',
        'section__course_offering__course',
    )


class CourseSectionListView(SchoolScopedAdminAPIView):
    serializer_class = CourseSectionSerializer
    professional_school_lookup = 'course_offering__course__professional_school_id'

    def get(self, request: Request) -> Response:
        sections = self.get_scoped_queryset(
            request,
            course_section_queryset(),
        )

        return success_response(
            data={
                'course_sections': CourseSectionSerializer(
                    sections,
                    many=True,
                ).data,
            },
            request_id=request.request_id,
        )

    def post(self, request: Request) -> Response:
        serializer = CourseSectionWriteSerializer(
            data=request.data,
            context=self.get_write_serializer_context(request),
        )
        serializer.is_valid(raise_exception=True)
        section = serializer.save()

        return success_response(
            data=CourseSectionSerializer(section).data,
            request_id=request.request_id,
            status_code=status.HTTP_201_CREATED,
        )


class CourseSectionDetailView(SchoolScopedAdminAPIView):
    serializer_class = CourseSectionWriteSerializer
    professional_school_lookup = 'course_offering__course__professional_school_id'

    def patch(
        self,
        request: Request,
        section_id: UUID,
    ) -> Response:
        section = get_object_or_404(
            self.get_scoped_queryset(
                request,
                course_section_queryset(),
            ),
            public_id=section_id,
        )
        serializer = CourseSectionWriteSerializer(
            section,
            data=request.data,
            partial=True,
            context=self.get_write_serializer_context(request),
        )
        serializer.is_valid(raise_exception=True)
        updated_section = serializer.save()

        return success_response(
            data=CourseSectionSerializer(updated_section).data,
            request_id=request.request_id,
        )


class ClassMeetingListView(SchoolScopedAdminAPIView):
    serializer_class = ClassMeetingSerializer
    professional_school_lookup = (
        'section__course_offering__course__professional_school_id'
    )

    def get(self, request: Request) -> Response:
        meetings = self.get_scoped_queryset(
            request,
            class_meeting_queryset(),
        )

        return success_response(
            data={
                'class_meetings': ClassMeetingSerializer(
                    meetings,
                    many=True,
                ).data,
            },
            request_id=request.request_id,
        )

    def post(self, request: Request) -> Response:
        serializer = ClassMeetingWriteSerializer(
            data=request.data,
            context=self.get_write_serializer_context(request),
        )
        serializer.is_valid(raise_exception=True)
        meeting = serializer.save()

        return success_response(
            data=ClassMeetingSerializer(meeting).data,
            request_id=request.request_id,
            status_code=status.HTTP_201_CREATED,
        )


class ClassMeetingDetailView(SchoolScopedAdminAPIView):
    serializer_class = ClassMeetingWriteSerializer
    professional_school_lookup = (
        'section__course_offering__course__professional_school_id'
    )

    def patch(
        self,
        request: Request,
        meeting_id: UUID,
    ) -> Response:
        meeting = get_object_or_404(
            self.get_scoped_queryset(
                request,
                class_meeting_queryset(),
            ),
            public_id=meeting_id,
        )
        serializer = ClassMeetingWriteSerializer(
            meeting,
            data=request.data,
            partial=True,
            context=self.get_write_serializer_context(request),
        )
        serializer.is_valid(raise_exception=True)
        updated_meeting = serializer.save()

        return success_response(
            data=ClassMeetingSerializer(updated_meeting).data,
            request_id=request.request_id,
        )
