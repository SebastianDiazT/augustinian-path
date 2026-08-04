from django.urls import path

from .admin_views import PlatformAdminFacultyListView

app_name = 'academics-admin'

urlpatterns = [
    path(
        'faculties/',
        PlatformAdminFacultyListView.as_view(),
        name='faculty-list',
    ),
]
