from django.db import models

from apps.core.models import CatalogBaseModel


class Faculty(CatalogBaseModel):
    """Representa una Facultad (ej. Facultad de Ingeniería de Producción y Servicios)."""

    class AcademicArea(models.TextChoices):
        BIOMEDICAS = 'biomedicas', 'Ciencias Biomédicas'
        INGENIERIAS = 'ingenierias', 'Ingenierías'
        SOCIALES = 'sociales', 'Ciencias Sociales'

    name = models.CharField(max_length=255, unique=True)
    acronym = models.CharField(max_length=20, unique=True, help_text='Ej. FIPS')

    # Añadimos el área aquí como un campo fijo
    area = models.CharField(
        max_length=20,
        choices=AcademicArea.choices,
        help_text='Área académica general de la universidad.',
    )

    description = models.TextField(blank=True)

    class Meta:
        db_table = 'institution_faculty'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_area_display()})'


class ProfessionalSchool(CatalogBaseModel):
    """Representa una Escuela Profesional (ej. Escuela Profesional de Ingeniería de Sistemas)."""

    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT, related_name='schools')
    name = models.CharField(max_length=255, unique=True)
    acronym = models.CharField(max_length=20, unique=True, help_text='Ej. EPIS')
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'institution_professional_school'
        ordering = ['name']

    def __str__(self):
        return self.name
