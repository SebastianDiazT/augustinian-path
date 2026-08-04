from django.urls import path

from .admin_views import (
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
]
