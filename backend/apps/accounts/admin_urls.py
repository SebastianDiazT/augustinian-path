from django.urls import path

from .admin_views import PlatformAdminAccessView

app_name = 'accounts-admin'

urlpatterns = [
    path(
        'access/',
        PlatformAdminAccessView.as_view(),
        name='access',
    ),
]
