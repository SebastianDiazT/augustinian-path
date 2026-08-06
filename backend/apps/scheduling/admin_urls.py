from django.urls import path

from .admin_views import (
    ClassMeetingDetailView,
    ClassMeetingListView,
    CourseSectionDetailView,
    CourseSectionListView,
)

app_name = 'scheduling-admin'

urlpatterns = [
    path(
        'course-sections/',
        CourseSectionListView.as_view(),
        name='course-section-list',
    ),
    path(
        'course-sections/<uuid:section_id>/',
        CourseSectionDetailView.as_view(),
        name='course-section-detail',
    ),
    path(
        'class-meetings/',
        ClassMeetingListView.as_view(),
        name='class-meeting-list',
    ),
    path(
        'class-meetings/<uuid:meeting_id>/',
        ClassMeetingDetailView.as_view(),
        name='class-meeting-detail',
    ),
]
