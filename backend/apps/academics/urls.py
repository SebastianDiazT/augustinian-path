from django.urls import path

from .views import (
    CurriculumPlanCatalogListView,
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
    path(
        'curriculum-plans/',
        CurriculumPlanCatalogListView.as_view(),
        name='curriculum-plan-list',
    ),
]
