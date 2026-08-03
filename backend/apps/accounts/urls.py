from django.urls import path

from .views import CSRFView, CurrentUserView, LogoutView

app_name = 'accounts'

urlpatterns = [
    path('csrf/', CSRFView.as_view(), name='csrf'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
