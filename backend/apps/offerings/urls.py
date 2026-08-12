from rest_framework.routers import DefaultRouter

from .views import OfferingViewSet, SectionViewSet, TimeBlockViewSet

app_name = 'offerings'

router = DefaultRouter()
router.register('offerings', OfferingViewSet, basename='offering')
router.register('sections', SectionViewSet, basename='section')
router.register('time-blocks', TimeBlockViewSet, basename='time-block')

urlpatterns = router.urls
