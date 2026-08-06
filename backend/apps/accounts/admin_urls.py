from django.urls import path

from .admin_views import (
    PlatformAdminAcademicAdminAssignmentView,
    PlatformAdminAccessView,
    PlatformAdminUserListView,
)

app_name = 'accounts-admin'

urlpatterns = [
    path(
        'access/',
        PlatformAdminAccessView.as_view(),
        name='access',
    ),
    path(
        'users/',
        PlatformAdminUserListView.as_view(),
        name='users',
    ),
    path(
        ('users/<uuid:user_id>/academic-admin-assignment/'),
        PlatformAdminAcademicAdminAssignmentView.as_view(),
        name='user-academic-admin-assignment',
    ),
]
