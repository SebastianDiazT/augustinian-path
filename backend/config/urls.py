from django.conf import settings
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

api_prefix = f'api/{settings.API_VERSION}/'

urlpatterns = [
    path(api_prefix, include('apps.core.urls', namespace='core')),
    path(f'{api_prefix}institution/', include('apps.institution.urls', namespace='institution')),
    path(f'{api_prefix}curricula/', include('apps.curricula.urls', namespace='curricula')),
    # path(f'{api_prefix}offerings/', include('apps.offerings.urls', namespace='offerings')),
    path(f'{api_prefix}accounts/', include('apps.accounts.urls', namespace='accounts')),
    # path(
    #     f'{api_prefix}academic-records/',
    #     include('apps.academic_records.urls', namespace='academic_records'),
    # ),
    # path(f'{api_prefix}schedules/', include('apps.schedules.urls', namespace='schedules')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
