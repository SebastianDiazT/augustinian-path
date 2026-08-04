from django.urls import path

from .admin_views import (
    PlatformAdminCourseDetailView,
    PlatformAdminCourseListView,
    PlatformAdminCurriculumCourseDetailView,
    PlatformAdminCurriculumCourseListView,
    PlatformAdminCurriculumPlanDetailView,
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
        'curriculum-plans/<uuid:plan_id>/',
        PlatformAdminCurriculumPlanDetailView.as_view(),
        name='curriculum-plan-detail',
    ),
    path(
        'courses/',
        PlatformAdminCourseListView.as_view(),
        name='course-list',
    ),
    path(
        'courses/<uuid:course_id>/',
        PlatformAdminCourseDetailView.as_view(),
        name='course-detail',
    ),
    path(
        'curriculum-courses/',
        PlatformAdminCurriculumCourseListView.as_view(),
        name='curriculum-course-list',
    ),
    path(
        'curriculum-courses/<uuid:curriculum_course_id>/',
        PlatformAdminCurriculumCourseDetailView.as_view(),
        name='curriculum-course-detail',
    ),
]
