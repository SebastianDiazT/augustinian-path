from django.urls import path

from .views import SyllabusCatalogView, SyllabusDetailView

app_name = 'syllabi'

urlpatterns = [
    path(
        '',
        SyllabusCatalogView.as_view(),
        name='syllabus-list',
    ),
    path(
        '<uuid:syllabus_id>/',
        SyllabusDetailView.as_view(),
        name='syllabus-detail',
    ),
]
