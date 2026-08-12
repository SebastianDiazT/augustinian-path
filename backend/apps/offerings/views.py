from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsPlatformAdmin, IsSchoolDelegate

from .models import Meeting, Offering, Section, TimeBlock
from .serializers import (
    MeetingSerializer,
    OfferingSerializer,
    SectionSerializer,
    TimeBlockSerializer,
    validate_meeting_count_matches_course_hours,
)


class _IsAdminOrDelegateOfRelatedSchool(IsSchoolDelegate):
    def has_object_permission(self, request, view, obj):
        if request.user.is_platform_admin:
            return True
        return super().has_object_permission(request, view, obj)


class _CatalogWritePermissionMixin:
    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        if self.action == 'create':
            return [IsPlatformAdmin()]
        return [IsAuthenticated(), _IsAdminOrDelegateOfRelatedSchool()]


class OfferingViewSet(_CatalogWritePermissionMixin, viewsets.ModelViewSet):
    queryset = Offering.objects.filter(is_active=True).select_related('course', 'academic_term')
    serializer_class = OfferingSerializer
    lookup_field = 'public_id'
    filterset_fields = ['course', 'academic_term']


class SectionViewSet(_CatalogWritePermissionMixin, viewsets.ModelViewSet):
    queryset = (
        Section.objects.filter(is_active=True)
        .select_related(
            'offering__course',
            'instructor',
        )
        .prefetch_related('meetings__time_block')
    )
    serializer_class = SectionSerializer
    lookup_field = 'public_id'
    filterset_fields = ['offering', 'section_type']

    @extend_schema(
        request=MeetingSerializer(many=True),
        responses=SectionSerializer,
    )
    @action(detail=True, methods=['put'])
    def meetings(self, request, public_id=None):
        section = self.get_object()
        validate_meeting_count_matches_course_hours(section, request.data)

        serializer = MeetingSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            section.meetings.all().delete()
            new_meetings = [Meeting(section=section, **item) for item in serializer.validated_data]
            Meeting.objects.bulk_create(new_meetings)

        section.refresh_from_db()
        return Response(SectionSerializer(section).data)


class TimeBlockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TimeBlock.objects.filter(is_active=True)
    serializer_class = TimeBlockSerializer
    lookup_field = 'public_id'
    permission_classes = [IsAuthenticated]
