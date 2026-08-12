from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.core.urls', namespace='core')),
    path('api/v1/institution/', include('apps.institution.urls', namespace='institution')),
    path('api/v1/curricula/', include('apps.curricula.urls', namespace='curricula')),
    # path('api/v1/offerings/', include('apps.offerings.urls', namespace='offerings')),
    path('api/v1/accounts/', include('apps.accounts.urls', namespace='accounts')),
    # path(
    #     'api/v1/academic-records/',
    #     include('apps.academic_records.urls', namespace='academic_records'),
    # ),
    # path('api/v1/schedules/', include('apps.schedules.urls', namespace='schedules')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
