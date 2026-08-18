from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticated

from .models import Faculty, ProfessionalSchool
from .serializers import FacultySerializer, ProfessionalSchoolSerializer


class FacultyCatalogListView(generics.ListAPIView):
    """
    GET: Lista facultades activas para poblar selectores en React.
    Sin paginación para evitar que los dropdowns se corten.
    """

    serializer_class = FacultySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'acronym']
    pagination_class = None

    def get_queryset(self):
        qs = Faculty.objects.filter(is_active=True).order_by('name')
        area = self.request.query_params.get('area')
        if area:
            qs = qs.filter(area=area)
        return qs


class SchoolCatalogListView(generics.ListAPIView):
    """
    GET: Lista escuelas activas para poblar selectores.
    Sin paginación.
    """

    serializer_class = ProfessionalSchoolSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'acronym']
    pagination_class = None

    def get_queryset(self):
        qs = (
            ProfessionalSchool.objects.filter(is_active=True)
            .select_related('faculty')
            .order_by('name')
        )
        faculty_id = self.request.query_params.get('faculty')
        if faculty_id:
            qs = qs.filter(faculty__public_id=faculty_id)
        return qs
