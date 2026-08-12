from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AcademicProgressView, CourseEnrollmentViewSet, EligibleCoursesView

app_name = 'academic_records'

router = DefaultRouter()
router.register('course-enrollments', CourseEnrollmentViewSet, basename='course-enrollment')

urlpatterns = router.urls + [
    path('progress/', AcademicProgressView.as_view(), name='progress'),
    path('eligible-courses/', EligibleCoursesView.as_view(), name='eligible-courses'),
]
