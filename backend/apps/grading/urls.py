from django.urls import path

from .views import EvaluationSchemeCatalogView, GradeSimulationView

app_name = 'grading'

urlpatterns = [
    path(
        'schemes/',
        EvaluationSchemeCatalogView.as_view(),
        name='evaluation-scheme-list',
    ),
    path(
        'schemes/<uuid:scheme_id>/simulate/',
        GradeSimulationView.as_view(),
        name='grade-simulation',
    ),
]
