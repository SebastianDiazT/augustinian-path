from django.urls import path

from .views import (
    FacultyCatalogListView,
    ProfessionalSchoolCatalogListView,
)

app_name = 'academics'

urlpatterns = [
    path(
        'faculties/',
        FacultyCatalogListView.as_view(),
        name='faculty-list',
    ),
    path(
        'professional-schools/',
        ProfessionalSchoolCatalogListView.as_view(),
        name='professional-school-list',
    ),
]
