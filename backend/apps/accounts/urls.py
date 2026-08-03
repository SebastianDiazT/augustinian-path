from django.urls import path

from .views import CSRFView, CurrentUserView

app_name = 'accounts'

urlpatterns = [
    path('csrf/', CSRFView.as_view(), name='csrf'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
]
