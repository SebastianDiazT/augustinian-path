from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.core.models import CatalogBaseModel

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, CatalogBaseModel):
    """Platform identity.

    - is_staff: Django admin access.
    - is_superuser: inherited from PermissionsMixin, all Django
      permissions (independent of is_platform_admin).
    - is_platform_admin: Ruta Agustina's business-level "platform admin"
      role (full API access). Not to be confused with is_superuser.
    - The "student" and "delegate" roles do NOT live here as a field:
      they're implicit, derived from having a StudentProfile (see
      `is_student`) or an active SchoolDelegation (see `is_delegate_of`).
      This lets the same person be admin, delegate, and student at the
      same time, with no conflict, as defined in the project brief.
    """

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    google_sub = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text=(
            "The Google account's 'sub' identifier. Empty for accounts "
            'created only for the Django admin.'
        ),
    )
    is_platform_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.email

    @property
    def is_student(self):
        return hasattr(self, 'student_profile')

    def is_delegate_of(self, school):
        return self.delegations.filter(school=school, is_active=True).exists()


class StudentProfile(CatalogBaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
    )
    # CUI: Código Único de Identificación, the student ID code issued by
    # UNSA. Kept untranslated since it's the official identifier's name.
    cui = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='CUI',
        help_text='Código Único de Identificación del estudiante.',
    )

    class Meta:
        db_table = 'accounts_student_profile'
        verbose_name = 'Perfil de estudiante'
        verbose_name_plural = 'Perfiles de estudiante'

    def __str__(self):
        return f'{self.user.email} (CUI {self.cui})'


class SchoolMembership(CatalogBaseModel):
    """A student's verified membership to a professional school.

    Only exists once verified: created exclusively when approving a
    MembershipRequest (see MembershipRequestViewSet.approve). The student
    never edits or creates it directly.
    """

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    school = models.ForeignKey(
        'institution.ProfessionalSchool',
        on_delete=models.PROTECT,
        related_name='memberships',
    )
    curriculum_plan = models.ForeignKey(
        'curricula.CurriculumPlan',
        on_delete=models.PROTECT,
        related_name='memberships',
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='memberships_verified',
    )
    verified_at = models.DateTimeField()

    class Meta:
        db_table = 'accounts_school_membership'
        verbose_name = 'Membresía de escuela'
        verbose_name_plural = 'Membresías de escuela'
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'school'],
                name='unique_membership_per_school',
            ),
        ]

    def __str__(self):
        return f'{self.student} → {self.school}'


class MembershipRequest(CatalogBaseModel):
    class RequestType(models.TextChoices):
        INITIAL_REQUEST = 'initial_request', 'Solicitud inicial'
        ADD_SECOND_PROGRAM = 'add_second_program', 'Agregar segunda carrera'
        ERROR_CORRECTION = 'error_correction', 'Corrección por error'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        APPROVED = 'approved', 'Aprobada'
        REJECTED = 'rejected', 'Rechazada'

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='membership_requests',
    )
    school = models.ForeignKey(
        'institution.ProfessionalSchool',
        on_delete=models.PROTECT,
        related_name='membership_requests',
    )
    curriculum_plan = models.ForeignKey(
        'curricula.CurriculumPlan',
        on_delete=models.PROTECT,
        related_name='membership_requests',
    )
    request_type = models.CharField(max_length=30, choices=RequestType.choices)
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
    )
    evidence_url = models.URLField(blank=True)
    resolution_comment = models.TextField(blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='membership_requests_resolved',
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'accounts_membership_request'
        verbose_name = 'Solicitud de membresía'
        verbose_name_plural = 'Solicitudes de membresía'

    def __str__(self):
        return f'{self.student} → {self.school} ({self.status})'


class SchoolDelegation(CatalogBaseModel):
    delegate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='delegations',
    )
    school = models.ForeignKey(
        'institution.ProfessionalSchool',
        on_delete=models.CASCADE,
        related_name='delegations',
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='delegations_assigned',
    )

    class Meta:
        db_table = 'accounts_school_delegation'
        verbose_name = 'Delegación de escuela'
        verbose_name_plural = 'Delegaciones de escuela'
        constraints = [
            models.UniqueConstraint(
                fields=['delegate', 'school'],
                name='unique_delegation_per_school',
            ),
        ]

    def __str__(self):
        return f'{self.delegate} — {self.school}'
