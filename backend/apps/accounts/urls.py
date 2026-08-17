from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .auth_views import GoogleLoginView
from .views_student import (
    StudentMembershipRequestView,
    StudentProfileMeView,
    StudentSupportTicketView,
)

app_name = 'accounts'

urlpatterns = [
    # Autenticación
    path('auth/google/', GoogleLoginView.as_view(), name='auth-google'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),

    # Estudiante (Onboarding)
    path('student/me/', StudentProfileMeView.as_view(), name='student-me'),
    path(
        'student/membership-requests/',
        StudentMembershipRequestView.as_view(),
        name='student-membership-requests',
    ),
    path(
        'student/support-tickets/',
        StudentSupportTicketView.as_view(),
        name='student-support-tickets',
    ),
]
