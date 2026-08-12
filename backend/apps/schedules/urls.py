from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    PublicScheduleView,
    PublicShareLinkViewSet,
    ScheduleAlternativeViewSet,
    ScheduleSimulationViewSet,
)

app_name = 'schedules'

router = DefaultRouter()
router.register('schedule-simulations', ScheduleSimulationViewSet, basename='schedule-simulation')
router.register(
    'schedule-alternatives',
    ScheduleAlternativeViewSet,
    basename='schedule-alternative'
)
router.register('share-links', PublicShareLinkViewSet, basename='share-link')

urlpatterns = router.urls + [
    path('public/<uuid:public_id>/', PublicScheduleView.as_view(), name='public-schedule'),
]
