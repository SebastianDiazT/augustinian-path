from django.db import models

from apps.core.models import CatalogBaseModel


class Area(CatalogBaseModel):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'institution_area'
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'

    def __str__(self):
        return self.name


class Faculty(CatalogBaseModel):
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='faculties')
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'institution_faculty'
        verbose_name = 'Facultad'
        verbose_name_plural = 'Facultades'
        constraints = [
            models.UniqueConstraint(
                fields=['area', 'name'],
                name='unique_faculty_name_per_area',
            ),
        ]

    def __str__(self):
        return self.name


class ProfessionalSchool(CatalogBaseModel):
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.PROTECT,
        related_name='professional_schools',
    )
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'institution_professional_school'
        verbose_name = 'Escuela Profesional'
        verbose_name_plural = 'Escuelas Profesionales'
        constraints = [
            models.UniqueConstraint(
                fields=['faculty', 'name'],
                name='unique_school_name_per_faculty',
            ),
        ]

    def __str__(self):
        return self.name

    def get_school(self):
        return self
