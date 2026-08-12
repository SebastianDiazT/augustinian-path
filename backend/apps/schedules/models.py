from django.db import models

from apps.core.models import CatalogBaseModel


class ScheduleSimulation(CatalogBaseModel):
    """One run of the generator: which courses/preferences were used to
    produce a set of ScheduleAlternative results. Every run is kept (not
    overwritten), so a student can come back and compare past attempts
    with different preferences."""

    student = models.ForeignKey(
        'accounts.StudentProfile', on_delete=models.CASCADE, related_name='schedule_simulations',
    )
    academic_term = models.ForeignKey(
        'curricula.AcademicTerm', on_delete=models.PROTECT, related_name='schedule_simulations',
    )
    offerings = models.ManyToManyField(
        'offerings.Offering', related_name='schedule_simulations',
    )
    # Free-form request payload: excluded_sections, excluded_instructors,
    # preferred_free_days, time_of_day_range, minimize_gaps,
    # preferred_instructors, etc. Kept as JSON rather than a dozen
    # nullable columns, since this is input we replay/display, not
    # something we query by field.
    preferences = models.JSONField(default=dict, blank=True)
    # Notes about any automatic exclusion the generator had to make (the
    # "curso crítico" tie-break) — empty if nothing was excluded.
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'schedules_schedule_simulation'
        verbose_name = 'Simulación de Horario'
        verbose_name_plural = 'Simulaciones de Horario'

    def __str__(self):
        return f'{self.student} — {self.academic_term} ({self.created_at:%Y-%m-%d %H:%M})'


class ScheduleAlternative(CatalogBaseModel):
    simulation = models.ForeignKey(
        ScheduleSimulation, on_delete=models.CASCADE, related_name='alternatives',
    )
    score = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    rank = models.PositiveSmallIntegerField(help_text='1 = best, up to 4.')
    is_favorite = models.BooleanField(default=False)

    class Meta:
        db_table = 'schedules_schedule_alternative'
        verbose_name = 'Alternativa de Horario'
        verbose_name_plural = 'Alternativas de Horario'
        ordering = ['rank']
        constraints = [
            models.UniqueConstraint(
                fields=['simulation', 'rank'], name='unique_rank_per_simulation',
            ),
        ]

    def __str__(self):
        return f'{self.simulation} — #{self.rank} ({self.score})'


class ScheduleAlternativeSection(models.Model):
    """Bridge table: which Sections make up a given alternative. Not a
    CatalogBaseModel — it's a pure association row, no public_id/
    is_active/timestamps needed of its own."""

    alternative = models.ForeignKey(
        ScheduleAlternative, on_delete=models.CASCADE, related_name='sections',
    )
    section = models.ForeignKey(
        'offerings.Section', on_delete=models.PROTECT, related_name='schedule_alternatives',
    )

    class Meta:
        db_table = 'schedules_schedule_alternative_section'
        constraints = [
            models.UniqueConstraint(
                fields=['alternative', 'section'], name='unique_section_per_alternative',
            ),
        ]

    def __str__(self):
        return f'{self.alternative} — {self.section}'


class PublicShareLink(CatalogBaseModel):
    """Read-only, unauthenticated access to a single ScheduleAlternative.
    `public_id` (a UUID) doubles as the unguessable share token — no
    separate token field needed. Never expires; the student can revoke
    it at any time by setting `is_active=False` ('dejar de compartir'),
    which is the only way it stops working."""

    alternative = models.ForeignKey(
        ScheduleAlternative, on_delete=models.CASCADE, related_name='share_links',
    )
    include_personal_info = models.BooleanField(default=False)

    class Meta:
        db_table = 'schedules_public_share_link'
        verbose_name = 'Enlace Público de Horario'
        verbose_name_plural = 'Enlaces Públicos de Horario'

    def __str__(self):
        return f'Share link for {self.alternative}'
