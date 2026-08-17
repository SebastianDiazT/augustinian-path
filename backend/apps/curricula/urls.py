from django.urls import path

from .views_catalog import CourseMeshListView, PlanCatalogListView
from .views_management import (
    ManagementCourseDetailView,
    ManagementCourseListCreateView,
    ManagementPlanDetailView,
    ManagementPlanListCreateView,
    ManagementPrerequisiteDetailView,
    ManagementPrerequisiteListCreateView,
)

app_name = 'curricula'

urlpatterns = [
    # --- CATÁLOGO Y GRAFO (Lectura Estudiantes) ---
    path('catalog/plans/', PlanCatalogListView.as_view(), name='catalog-plans'),
    path('catalog/mesh/', CourseMeshListView.as_view(), name='catalog-mesh'),
    # --- GESTIÓN DE DELEGADOS / ADMINS (CRUD) ---
    # Planes
    path('management/plans/', ManagementPlanListCreateView.as_view(), name='management-plans-list'),
    path(
        'management/plans/<uuid:public_id>/',
        ManagementPlanDetailView.as_view(),
        name='management-plans-detail',
    ),
    # Cursos
    path(
        'management/courses/',
        ManagementCourseListCreateView.as_view(),
        name='management-courses-list',
    ),
    path(
        'management/courses/<uuid:public_id>/',
        ManagementCourseDetailView.as_view(),
        name='management-courses-detail',
    ),
    # Prerrequisitos
    path(
        'management/prerequisites/',
        ManagementPrerequisiteListCreateView.as_view(),
        name='management-prereqs-list',
    ),
    path(
        'management/prerequisites/<uuid:public_id>/',
        ManagementPrerequisiteDetailView.as_view(),
        name='management-prereqs-detail',
    ),
]
