from rest_framework.routers import DefaultRouter

from .views import AreaViewSet, FacultyViewSet, ProfessionalSchoolViewSet

app_name = 'institution'

router = DefaultRouter()
router.register('areas', AreaViewSet, basename='area')
router.register('faculties', FacultyViewSet, basename='faculty')
router.register('professional-schools', ProfessionalSchoolViewSet, basename='professional-school')

urlpatterns = router.urls
