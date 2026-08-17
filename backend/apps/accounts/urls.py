from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .auth_views import GoogleLoginView
from .views_management import (
    DelegateMembershipRequestActionView,
    DelegateMembershipRequestListView,
    DelegateSupportTicketActionView,
    DelegateSupportTicketListView,
    ManagementSchoolDelegationDetailView,
    ManagementSchoolDelegationListView,
)
from .views_student import (
    StudentMembershipRequestView,
    StudentProfileMeView,
    StudentSupportTicketView,
)

app_name = 'accounts'

urlpatterns = [
    # 1. Autenticación
    path('auth/google/', GoogleLoginView.as_view(), name='auth-google'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),

    # 2. Estudiante (Cara al cliente)
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

    # 3. Administración / Delegados (Bandeja de entrada)
    path(
        'management/membership-requests/',
        DelegateMembershipRequestListView.as_view(),
        name='management-requests-list',
    ),
    path(
        'management/membership-requests/<uuid:public_id>/action/',
        DelegateMembershipRequestActionView.as_view(),
        name='management-requests-action',
    ),
    path(
        'management/support-tickets/',
        DelegateSupportTicketListView.as_view(),
        name='management-tickets-list',
    ),
    path(
        'management/support-tickets/<uuid:public_id>/action/',
        DelegateSupportTicketActionView.as_view(),
        name='management-tickets-action',
    ),

    # 4. Asignación de Roles (Exclusivo Admin)
    path(
        'management/delegations/',
        ManagementSchoolDelegationListView.as_view(),
        name='management-delegations-list',
    ),
    path(
        'management/delegations/<uuid:public_id>/',
        ManagementSchoolDelegationDetailView.as_view(),
        name='management-delegations-detail',
    ),
]
