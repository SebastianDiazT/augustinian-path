from rest_framework.routers import DefaultRouter

from .views import (
    AcademicTermViewSet,
    CourseViewSet,
    CurriculumPlanViewSet,
    ElectiveBranchViewSet,
    InstructorViewSet,
    PrerequisiteViewSet,
    SyllabusViewSet,
)

app_name = 'curricula'

router = DefaultRouter()
router.register('curriculum-plans', CurriculumPlanViewSet, basename='curriculum-plan')
router.register('elective-branches', ElectiveBranchViewSet, basename='elective-branch')
router.register('courses', CourseViewSet, basename='course')
router.register('prerequisites', PrerequisiteViewSet, basename='prerequisite')
router.register('academic-terms', AcademicTermViewSet, basename='academic-term')
router.register('instructors', InstructorViewSet, basename='instructor')
router.register('syllabi', SyllabusViewSet, basename='syllabus')

urlpatterns = router.urls
