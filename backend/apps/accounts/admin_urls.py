from django.urls import path

from .admin_views import (
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
]
