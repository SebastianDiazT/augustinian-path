from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from apps.core.constants import API_PATH_PREFIX

api_urlpatterns = [
    path('', include('apps.core.urls')),
    path(
        'auth/',
        include('apps.accounts.urls'),
    ),
    path(
        'admin/',
        include('apps.accounts.admin_urls'),
    ),
    path(
        'admin/',
        include('apps.academics.admin_urls'),
    ),
    path(
        'academics/',
        include('apps.academics.urls'),
    ),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        API_PATH_PREFIX,
        include(api_urlpatterns),
    ),
    path(
        'accounts/',
        include('allauth.urls'),
    ),
    path(
        '_allauth/',
        include('allauth.headless.urls'),
    ),
    path(
        'api/schema/',
        SpectacularAPIView.as_view(),
        name='schema',
    ),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(
            url_name='schema',
        ),
        name='swagger-ui',
    ),
]
