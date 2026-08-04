from django.urls import path

from .admin_views import (
    PlatformAdminCourseListView,
    PlatformAdminCurriculumCourseListView,
    PlatformAdminCurriculumPlanListView,
    PlatformAdminFacultyDetailView,
    PlatformAdminFacultyListView,
    PlatformAdminProfessionalSchoolDetailView,
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
        'faculties/<uuid:faculty_id>/',
        PlatformAdminFacultyDetailView.as_view(),
        name='faculty-detail',
    ),
    path(
        'professional-schools/',
        PlatformAdminProfessionalSchoolListView.as_view(),
        name='professional-school-list',
    ),
    path(
        'professional-schools/<uuid:school_id>/',
        PlatformAdminProfessionalSchoolDetailView.as_view(),
        name='professional-school-detail',
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
