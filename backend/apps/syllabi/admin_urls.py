from django.urls import path

from .admin_views import SyllabusDetailView, SyllabusListView

app_name = 'syllabi-admin'

urlpatterns = [
    path(
        'syllabi/',
        SyllabusListView.as_view(),
        name='syllabus-list',
    ),
    path(
        'syllabi/<uuid:syllabus_id>/',
        SyllabusDetailView.as_view(),
        name='syllabus-detail',
    ),
]
