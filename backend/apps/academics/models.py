from uuid import uuid4

from django.db import models
from django.db.models.functions import Lower


class Faculty(models.Model):
    """Facultad perteneciente a la Universidad Nacional de San Agustín."""

    public_id = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
    )
    name = models.CharField(
        max_length=150,
    )
    is_active = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'facultad'
        verbose_name_plural = 'facultades'
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                name='unique_faculty_name_case_insensitive',
            ),
            models.CheckConstraint(
                condition=~models.Q(name=''),
                name='faculty_name_not_empty',
            ),
        ]

    def save(self, *args, **kwargs) -> None:
        self.name = ' '.join(self.name.split())
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
