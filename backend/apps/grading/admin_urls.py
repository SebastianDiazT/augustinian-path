from django.urls import path

from .admin_views import (
    EvaluationComponentDetailView,
    EvaluationComponentListView,
    EvaluationSchemeListView,
)

app_name = 'grading-admin'

urlpatterns = [
    path(
        'evaluation-schemes/',
        EvaluationSchemeListView.as_view(),
        name='evaluation-scheme-list',
    ),
    path(
        'evaluation-components/',
        EvaluationComponentListView.as_view(),
        name='evaluation-component-list',
    ),
    path(
        'evaluation-components/<uuid:component_id>/',
        EvaluationComponentDetailView.as_view(),
        name='evaluation-component-detail',
    ),
]
