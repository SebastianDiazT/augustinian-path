from django.db import models

from apps.core.models import CatalogBaseModel


class CurriculumPlan(CatalogBaseModel):
    """Ej: Plan de Estudios 2017, Plan de Estudios 2025"""

    school = models.ForeignKey(
        'institution.ProfessionalSchool', on_delete=models.CASCADE, related_name='curriculum_plans'
    )
    name = models.CharField(max_length=255)
    year = models.PositiveIntegerField(help_text='Año del plan de estudios')

    class Meta:
        db_table = 'curricula_curriculum_plan'
        ordering = ['-year']

    def __str__(self):
        return f'{self.name} - {self.school.acronym}'


class ElectiveBranch(CatalogBaseModel):
    """Ej: Rama de Ciberseguridad, Rama de Videojuegos"""

    curriculum_plan = models.ForeignKey(
        CurriculumPlan, on_delete=models.CASCADE, related_name='elective_branches'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'curricula_elective_branch'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.curriculum_plan.year})'


class Course(CatalogBaseModel):
    class CourseType(models.TextChoices):
        MANDATORY = 'mandatory', 'Obligatorio'
        ELECTIVE = 'elective', 'Electivo'

    class AcademicArea(models.TextChoices):
        BASIC = 'A', 'Formación Básica'
        SPECIALIZED = 'B', 'Formación Especializada'
        PROFESSIONAL = 'C', 'Formación Profesional y Otros'
        GEN_LEARNING = 'D', 'Est.Gen.: Capacidades de Aprendizaje'
        GEN_HUMANITIES = 'E', 'Est.Gen.: Form.Humanist.Ident. y Ciudadania'
        SPECIFIC = 'F', 'Estudios Específicos'
        SPECIALTY = 'G', 'Estudios de Especialidad'

    curriculum_plan = models.ForeignKey(
        CurriculumPlan, on_delete=models.CASCADE, related_name='courses'
    )
    branch = models.ForeignKey(
        ElectiveBranch, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses'
    )

    code = models.CharField(max_length=20, help_text='Ej: 1701102 o 2504252')
    name = models.CharField(max_length=255)
    credits = models.DecimalField(max_digits=4, decimal_places=2)

    # Desglose de Horas
    theory_hours = models.PositiveIntegerField(default=0, verbose_name='Horas Teóricas (TEOR)')
    seminar_hours = models.PositiveIntegerField(default=0, verbose_name='Horas Seminario (SEMI)')
    theory_practice_hours = models.PositiveIntegerField(
        default=0, verbose_name='Horas Teórico-Prácticas (T.PR)'
    )
    practice_hours = models.PositiveIntegerField(default=0, verbose_name='Horas Prácticas (PRAC)')
    lab_hours = models.PositiveIntegerField(default=0, verbose_name='Horas Laboratorio (LAB)')

    cycle = models.PositiveIntegerField(help_text='Ciclo del 1 al 10')
    course_type = models.CharField(
        max_length=20, choices=CourseType.choices, default=CourseType.MANDATORY
    )

    academic_area = models.CharField(
        max_length=2,
        choices=AcademicArea.choices,
        help_text='Componente curricular (A, B, C, D, E, F, G)',
    )

    min_credits_required = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Créditos acumulados requeridos (ej. 190 para Proyecto Integrador)',
    )

    class Meta:
        db_table = 'curricula_course'
        ordering = ['cycle', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['curriculum_plan', 'code'], name='unique_course_code_per_plan'
            )
        ]

    def __str__(self):
        return f'{self.code} - {self.name}'

    @property
    def has_lab(self):
        return self.lab_hours > 0