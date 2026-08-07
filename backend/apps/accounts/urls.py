from django.urls import path

from .views import (
    CSRFView,
    CurrentUserView,
    GoogleLoginView,
    LogoutView,
    RefreshTokenView,
)

app_name = 'accounts'

urlpatterns = [
    path(
        'google/',
        GoogleLoginView.as_view(),
        name='google-login',
    ),
    path(
        'refresh/',
        RefreshTokenView.as_view(),
        name='refresh-token',
    ),
    path('csrf/', CSRFView.as_view(), name='csrf'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
