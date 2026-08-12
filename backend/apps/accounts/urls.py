from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .auth_views import GoogleLoginView
from .views import (
    MembershipRequestViewSet,
    SchoolDelegationViewSet,
    SchoolMembershipViewSet,
    StudentProfileViewSet,
)

app_name = 'accounts'

router = DefaultRouter()
router.register(
    'student-profiles',
    StudentProfileViewSet,
    basename='student-profile',
)
router.register(
    'school-memberships',
    SchoolMembershipViewSet,
    basename='school-membership',
)
router.register(
    'membership-requests',
    MembershipRequestViewSet,
    basename='membership-request',
)
router.register(
    'school-delegations',
    SchoolDelegationViewSet,
    basename='school-delegation',
)

urlpatterns = router.urls + [
    path('auth/google/', GoogleLoginView.as_view(), name='auth-google'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
]
