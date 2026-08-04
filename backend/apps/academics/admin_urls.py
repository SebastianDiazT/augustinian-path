from django.urls import path

from .admin_views import (
    PlatformAdminCourseListView,
    PlatformAdminCurriculumCourseListView,
    PlatformAdminCurriculumPlanListView,
    PlatformAdminFacultyListView,
    PlatformAdminProfessionalSchoolListView,
)

app_name = 'academics-admin'

urlpatterns = [
    path(
        'faculties/',
        PlatformAdminFacultyListView.as_view(),
        name='faculty-list',
    ),
    path(
        'professional-schools/',
        PlatformAdminProfessionalSchoolListView.as_view(),
        name='professional-school-list',
    ),
    path(
        'curriculum-plans/',
        PlatformAdminCurriculumPlanListView.as_view(),
        name='curriculum-plan-list',
    ),
    path(
        'courses/',
        PlatformAdminCourseListView.as_view(),
        name='course-list',
    ),
    path(
        'curriculum-courses/',
        PlatformAdminCurriculumCourseListView.as_view(),
        name='curriculum-course-list',
    ),
]
