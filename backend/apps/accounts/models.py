from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.core.models import CatalogBaseModel

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, CatalogBaseModel):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    google_sub = models.CharField(max_length=255, unique=True, null=True, blank=True)
    picture_url = models.URLField(blank=True)
    cui = models.CharField(max_length=20, unique=True, null=True, blank=True)

    is_platform_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.email} - {self.cui if self.cui else "Sin CUI"}'


class SupportTicket(CatalogBaseModel):
    """Buzón interno para correcciones de CUI y soporte general."""

    class IssueType(models.TextChoices):
        CUI_CORRECTION = 'cui_correction', 'Corrección de CUI'
        TECHNICAL_ISSUE = 'technical_issue', 'Problema Técnico'
        OTHER = 'other', 'Otro'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        RESOLVED = 'resolved', 'Resuelto'
        REJECTED = 'rejected', 'Rechazado'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    school = models.ForeignKey(
        'institution.ProfessionalSchool',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Opcional. Ayuda a enrutar el ticket al delegado correcto.',
    )
    issue_type = models.CharField(max_length=30, choices=IssueType.choices)
    message = models.TextField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)

    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets_resolved'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'accounts_support_ticket'
        ordering = ['-created_at']


class SchoolMembership(CatalogBaseModel):
    """Afiliación oficial del alumno a una escuela y malla curricular."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    school = models.ForeignKey(
        'institution.ProfessionalSchool', on_delete=models.PROTECT, related_name='memberships'
    )
    curriculum_plan = models.ForeignKey(
        'curricula.CurriculumPlan', on_delete=models.PROTECT, related_name='memberships'
    )

    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='memberships_verified'
    )
    verified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'accounts_school_membership'
        verbose_name = 'Membresía de escuela'
        verbose_name_plural = 'Membresías de escuela'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'school'], name='unique_membership_per_school'),
        ]


class MembershipRequest(CatalogBaseModel):
    """Solicitud de ingreso (Onboarding) que los delegados deben aprobar."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        APPROVED = 'approved', 'Aprobada'
        REJECTED = 'rejected', 'Rechazada'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='membership_requests')
    school = models.ForeignKey('institution.ProfessionalSchool', on_delete=models.PROTECT)
    curriculum_plan = models.ForeignKey('curricula.CurriculumPlan', on_delete=models.PROTECT)

    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    resolution_comment = models.TextField(blank=True)

    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'accounts_membership_request'
        verbose_name = 'Solicitud de membresía'
        verbose_name_plural = 'Solicitudes de membresía'
        ordering = ['-created_at']


class SchoolDelegation(CatalogBaseModel):
    """Permisos granulares: Quién administra qué escuela."""

    delegate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delegations')
    school = models.ForeignKey(
        'institution.ProfessionalSchool', on_delete=models.CASCADE, related_name='delegations'
    )
    assigned_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='delegations_assigned'
    )

    class Meta:
        db_table = 'accounts_school_delegation'
        verbose_name = 'Delegación de escuela'
        verbose_name_plural = 'Delegaciones de escuela'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['delegate', 'school'], name='unique_delegation_per_school'
            ),
        ]