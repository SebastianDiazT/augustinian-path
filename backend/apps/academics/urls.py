from django.urls import path

from .views import FacultyCatalogListView

app_name = 'academics'

urlpatterns = [
    path(
        'faculties/',
        FacultyCatalogListView.as_view(),
        name='faculty-list',
    ),
]
