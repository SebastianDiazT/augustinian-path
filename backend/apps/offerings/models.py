from django.db import models

from apps.core.models import CatalogBaseModel


class Offering(CatalogBaseModel):
    course = models.ForeignKey(
        'curricula.Course',
        on_delete=models.PROTECT,
        related_name='offerings',
    )
    academic_term = models.ForeignKey(
        'curricula.AcademicTerm',
        on_delete=models.PROTECT,
        related_name='offerings',
    )

    class Meta:
        db_table = 'offerings_offering'
        verbose_name = 'Oferta'
        verbose_name_plural = 'Ofertas'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'academic_term'],
                name='unique_offering_per_term',
            ),
        ]

    def __str__(self):
        return f'{self.course} — {self.academic_term}'

    def get_school(self):
        return self.course.get_school()


class Section(CatalogBaseModel):
    class SectionType(models.TextChoices):
        THEORY = 'theory', 'Teoría'
        LAB = 'lab', 'Laboratorio'

    offering = models.ForeignKey(
        Offering,
        on_delete=models.CASCADE,
        related_name='sections',
    )
    section_type = models.CharField(max_length=10, choices=SectionType.choices)
    number = models.CharField(max_length=10, help_text="E.g. 'A', 'B', '01'.")
    instructor = models.ForeignKey(
        'curricula.Instructor',
        on_delete=models.PROTECT,
        related_name='sections',
    )

    class Meta:
        db_table = 'offerings_section'
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'
        ordering = ['offering', 'section_type', 'number']
        constraints = [
            models.UniqueConstraint(
                fields=['offering', 'section_type', 'number'],
                name='unique_section_number_per_offering_and_type',
            ),
        ]

    def __str__(self):
        return f'{self.offering} — {self.get_section_type_display()} {self.number}'

    def get_school(self):
        return self.offering.get_school()

    @property
    def expected_meeting_count(self):
        course = self.offering.course
        if self.section_type == self.SectionType.THEORY:
            return (
                course.theory_hours
                + course.practice_hours
                + course.seminar_hours
                + course.theory_practice_hours
            )
        return course.lab_hours


class TimeBlock(CatalogBaseModel):
    order = models.PositiveSmallIntegerField(unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        db_table = 'offerings_time_block'
        verbose_name = 'Bloque Horario'
        verbose_name_plural = 'Bloques Horarios'
        ordering = ['order']

    def __str__(self):
        return f'{self.start_time:%H:%M}-{self.end_time:%H:%M}'


class Meeting(CatalogBaseModel):
    class DayOfWeek(models.TextChoices):
        MONDAY = 'monday', 'Lunes'
        TUESDAY = 'tuesday', 'Martes'
        WEDNESDAY = 'wednesday', 'Miércoles'
        THURSDAY = 'thursday', 'Jueves'
        FRIDAY = 'friday', 'Viernes'
        SATURDAY = 'saturday', 'Sábado'

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='meetings',
    )
    day_of_week = models.CharField(max_length=10, choices=DayOfWeek.choices)
    time_block = models.ForeignKey(
        TimeBlock,
        on_delete=models.PROTECT,
        related_name='meetings',
    )
    room = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'offerings_meeting'
        verbose_name = 'Reunión de Clase'
        verbose_name_plural = 'Reuniones de Clase'
        constraints = [
            models.UniqueConstraint(
                fields=['section', 'day_of_week', 'time_block'],
                name='unique_meeting_slot_per_section',
            ),
        ]

    def __str__(self):
        return f'{self.section} — {self.get_day_of_week_display()} {self.time_block}'
