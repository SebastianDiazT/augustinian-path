from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import CatalogBaseModel


class CurriculumPlan(CatalogBaseModel):
    school = models.ForeignKey(
        'institution.ProfessionalSchool',
        on_delete=models.PROTECT,
        related_name='curriculum_plans',
    )
    year = models.CharField(max_length=10)
    name = models.CharField(max_length=150, blank=True)
    min_elective_branches_to_complete = models.PositiveSmallIntegerField(
        default=2,
        help_text=(
            'Minimum number of distinct elective branches the student must '
            'complete (have at least one passed course in) to graduate.'
        ),
    )

    class Meta:
        db_table = 'curricula_curriculum_plan'
        verbose_name = 'Plan Curricular'
        verbose_name_plural = 'Planes Curriculares'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['school', 'year'],
                name='unique_plan_year_per_school',
            ),
        ]

    def __str__(self):
        return f'{self.school} — {self.year}'

    def get_school(self):
        return self.school


class ElectiveBranch(CatalogBaseModel):
    curriculum_plan = models.ForeignKey(
        CurriculumPlan,
        on_delete=models.CASCADE,
        related_name='elective_branches',
    )
    name = models.CharField(max_length=150)

    class Meta:
        db_table = 'curricula_elective_branch'
        verbose_name = 'Rama Electiva'
        verbose_name_plural = 'Ramas Electivas'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['curriculum_plan', 'name'],
                name='unique_branch_name_per_plan',
            ),
        ]

    def __str__(self):
        return f'{self.curriculum_plan} — {self.name}'

    def get_school(self):
        return self.curriculum_plan.school


class Course(CatalogBaseModel):
    class CourseType(models.TextChoices):
        MANDATORY = 'mandatory', 'Obligatorio'
        ELECTIVE = 'elective', 'Electivo'

    class AcademicArea(models.TextChoices):
        GENERAL_EDUCATION = 'general_education', 'Formación general'
        SPECIALTY = 'specialty', 'Especialidad'
        ELECTIVE = 'elective', 'Electivo'

    curriculum_plan = models.ForeignKey(
        CurriculumPlan,
        on_delete=models.CASCADE,
        related_name='courses',
    )
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    credits = models.DecimalField(max_digits=4, decimal_places=1)
    theory_hours = models.PositiveSmallIntegerField(default=0)
    practice_hours = models.PositiveSmallIntegerField(default=0)
    seminar_hours = models.PositiveSmallIntegerField(default=0)
    theory_practice_hours = models.PositiveSmallIntegerField(default=0)
    lab_hours = models.PositiveSmallIntegerField(default=0)

    cycle = models.PositiveSmallIntegerField(help_text='1-10, suggested cycle in the plan.')
    course_type = models.CharField(max_length=20, choices=CourseType.choices)
    academic_area = models.CharField(max_length=30, choices=AcademicArea.choices)

    branch = models.ForeignKey(
        ElectiveBranch,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='courses',
    )

    min_credits_required = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = 'curricula_course'
        verbose_name = 'Asignatura'
        verbose_name_plural = 'Asignaturas'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['curriculum_plan', 'code'],
                name='unique_course_code_per_plan',
            ),
        ]

    def __str__(self):
        return f'{self.code} — {self.name}'

    def get_school(self):
        return self.curriculum_plan.school

    @property
    def has_lab(self):
        return self.lab_hours > 0


class Prerequisite(CatalogBaseModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='prerequisites',
    )
    required_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='required_by',
    )

    class Meta:
        db_table = 'curricula_prerequisite'
        verbose_name = 'Prerrequisito'
        verbose_name_plural = 'Prerrequisitos'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'required_course'],
                name='unique_prerequisite_pair',
            ),
        ]

    def __str__(self):
        return f'{self.course} requiere {self.required_course}'

    def clean(self):
        if self.course_id == self.required_course_id:
            raise ValidationError('Un curso no puede ser prerrequisito de sí mismo.')
        if self.course.curriculum_plan_id != self.required_course.curriculum_plan_id:
            raise ValidationError(
                'El curso y su prerrequisito deben pertenecer al mismo plan curricular.',
            )

    def get_school(self):
        return self.course.get_school()


class AcademicTerm(CatalogBaseModel):
    code = models.CharField(max_length=10, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        db_table = 'curricula_academic_term'
        verbose_name = 'Periodo Académico'
        verbose_name_plural = 'Periodos Académicos'
        ordering = ['-created_at']

    def __str__(self):
        return self.code


class Instructor(CatalogBaseModel):
    full_name = models.CharField(max_length=200)

    class Meta:
        db_table = 'curricula_instructor'
        verbose_name = 'Docente'
        verbose_name_plural = 'Docentes'
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name


class Syllabus(CatalogBaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='syllabi')
    academic_term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.CASCADE,
        related_name='syllabi',
    )
    instructors = models.ManyToManyField(Instructor, related_name='syllabi')
    pdf_url = models.URLField(blank=True)

    description = models.TextField(blank=True)
    competencies = models.TextField(blank=True)
    thematic_content = models.TextField(blank=True)
    methodology = models.TextField(blank=True)
    evaluation_criteria = models.TextField(blank=True)
    weekly_plan = models.TextField(blank=True)
    bibliography = models.TextField(blank=True)
    resources = models.TextField(blank=True)
    lab_practice_info = models.TextField(blank=True)
    institutional_references = models.TextField(blank=True)

    class Meta:
        db_table = 'curricula_syllabus'
        verbose_name = 'Sílabo'
        verbose_name_plural = 'Sílabos'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'academic_term'],
                name='unique_syllabus_per_term',
            ),
        ]

    def __str__(self):
        return f'{self.course} — {self.academic_term}'

    def get_school(self):
        return self.course.curriculum_plan.school


class EvaluationComponent(CatalogBaseModel):
    syllabus = models.ForeignKey(
        Syllabus,
        on_delete=models.CASCADE,
        related_name='evaluation_components',
    )
    name = models.CharField(max_length=100)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    order = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'curricula_evaluation_component'
        verbose_name = 'Componente de Evaluación'
        verbose_name_plural = 'Componentes de Evaluación'
        ordering = ['syllabus', 'order']
        constraints = [
            models.UniqueConstraint(
                fields=['syllabus', 'order'],
                name='unique_component_order_per_syllabus',
            ),
        ]

    def __str__(self):
        return f'{self.name} ({self.weight}%)'
