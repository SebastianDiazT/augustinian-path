from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

handler404 = 'apps.core.error_views.custom_404_view'
handler500 = 'apps.core.error_views.custom_500_view'

api_v1_patterns = [
    path('', include('apps.core.urls')),
]

urlpatterns = [
    path('api/v1/', include(api_v1_patterns)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
