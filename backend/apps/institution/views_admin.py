from rest_framework import filters, generics

from apps.core.permissions import IsPlatformAdmin

from .models import Faculty, ProfessionalSchool
from .serializers import FacultySerializer, ProfessionalSchoolSerializer


class AdminFacultyListCreateView(generics.ListCreateAPIView):
    """GET: Lista todas las facultades (activas e inactivas). POST: Crea una nueva."""

    queryset = Faculty.all_objects.all().order_by('-created_at')
    serializer_class = FacultySerializer
    permission_classes = [IsPlatformAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'acronym', 'academic_area']


class AdminFacultyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE: Gestiona una facultad específica."""

    queryset = Faculty.all_objects.all()
    serializer_class = FacultySerializer
    permission_classes = [IsPlatformAdmin]
    lookup_field = 'public_id'

    def perform_destroy(self, instance):
        """Soft delete: En lugar de borrar la base de datos, la desactiva."""
        instance.is_active = False
        instance.save(update_fields=['is_active'])


class AdminSchoolListCreateView(generics.ListCreateAPIView):
    """GET: Lista todas las escuelas (activas e inactivas). POST: Crea una nueva."""

    queryset = (
        ProfessionalSchool.all_objects.all().select_related('faculty').order_by('-created_at')
    )
    serializer_class = ProfessionalSchoolSerializer
    permission_classes = [IsPlatformAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'acronym', 'faculty__name']

    def get_queryset(self):
        qs = super().get_queryset()
        faculty_id = self.request.query_params.get('faculty')
        if faculty_id:
            qs = qs.filter(faculty__public_id=faculty_id)
        return qs


class AdminSchoolDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE: Gestiona una escuela específica."""

    queryset = ProfessionalSchool.all_objects.all()
    serializer_class = ProfessionalSchoolSerializer
    permission_classes = [IsPlatformAdmin]
    lookup_field = 'public_id'

    def perform_destroy(self, instance):
        """Soft delete: En lugar de borrar la base de datos, la desactiva."""
        instance.is_active = False
        instance.save(update_fields=['is_active'])
