from django.urls import path

from .views import (
    AvailableCourseSectionListView,
    CourseEligibilityListView,
    ScenarioSelectionDetailView,
    ScenarioSelectionListView,
    ScheduleConflictListView,
    ScheduleScenarioDetailView,
    ScheduleScenarioListView,
)

app_name = 'scheduling'

urlpatterns = [
    path(
        'eligibility/',
        CourseEligibilityListView.as_view(),
        name='course-eligibility-list',
    ),
    path(
        'sections/',
        AvailableCourseSectionListView.as_view(),
        name='available-section-list',
    ),
    path(
        'scenarios/',
        ScheduleScenarioListView.as_view(),
        name='scenario-list',
    ),
    path(
        'scenarios/<uuid:scenario_id>/',
        ScheduleScenarioDetailView.as_view(),
        name='scenario-detail',
    ),
    path(
        'scenarios/<uuid:scenario_id>/selections/',
        ScenarioSelectionListView.as_view(),
        name='scenario-selection-list',
    ),
    path(
        'scenarios/<uuid:scenario_id>/selections/<uuid:selection_id>/',
        ScenarioSelectionDetailView.as_view(),
        name='scenario-selection-detail',
    ),
    path(
        'scenarios/<uuid:scenario_id>/conflicts/',
        ScheduleConflictListView.as_view(),
        name='scenario-conflict-list',
    ),
]
