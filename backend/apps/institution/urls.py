from django.urls import path

from .views_admin import (
    AdminFacultyDetailView,
    AdminFacultyListCreateView,
    AdminSchoolDetailView,
    AdminSchoolListCreateView,
)
from .views_catalog import FacultyCatalogListView, SchoolCatalogListView

app_name = 'institution'

urlpatterns = [
    # Catálogo Estudiantil (Solo Lectura) -> namespace: institution:catalog-faculties
    path('catalog/faculties/', FacultyCatalogListView.as_view(), name='catalog-faculties'),
    path('catalog/schools/', SchoolCatalogListView.as_view(), name='catalog-schools'),
    # Administración Global (CRUD) -> namespace: institution:admin-schools-detail
    path(
        'management/faculties/',
        AdminFacultyListCreateView.as_view(),
        name='management-faculties-list',
    ),
    path(
        'management/faculties/<uuid:public_id>/',
        AdminFacultyDetailView.as_view(),
        name='management-faculties-detail',
    ),
    path(
        'management/schools/', AdminSchoolListCreateView.as_view(), name='management-schools-list'
    ),
    path(
        'management/schools/<uuid:public_id>/',
        AdminSchoolDetailView.as_view(),
        name='management-schools-detail',
    ),
]
