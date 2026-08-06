from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q

from .google_identity import GoogleIdentity
from .models import User
from .roles import Role


class GoogleIdentityConflict(ValueError):
    """La identidad de Google entra en conflicto con otro usuario."""


@transaction.atomic
def synchronize_google_user(
    identity: GoogleIdentity,
) -> tuple[User, bool]:
    candidates = list(
        User.objects.select_for_update().filter(
            Q(google_subject=identity.subject) | Q(email=identity.email)
        )
    )

    subject_user = next(
        (user for user in candidates if user.google_subject == identity.subject),
        None,
    )
    email_user = next(
        (user for user in candidates if user.email == identity.email),
        None,
    )

    if (
        subject_user is not None
        and email_user is not None
        and subject_user.pk != email_user.pk
    ):
        raise GoogleIdentityConflict(
            'La identidad de Google pertenece a otro usuario.',
        )

    if subject_user is not None:
        user = subject_user
        created = False
    elif email_user is not None:
        if email_user.google_subject not in {
            None,
            identity.subject,
        }:
            raise GoogleIdentityConflict(
                'El correo institucional ya pertenece a otra identidad de Google.',
            )

        user = email_user
        created = False
    else:
        user = User.objects.create_user(
            email=identity.email,
            password=None,
            google_subject=identity.subject,
            first_name=identity.first_name,
            last_name=identity.last_name,
            avatar_url=identity.avatar_url,
        )
        created = True

    if not created:
        updated_fields = _synchronize_user_fields(
            user,
            identity,
        )

        if updated_fields:
            user.save(
                update_fields=updated_fields,
            )

    student_group = Group.objects.get(
        name=Role.STUDENT.value,
    )
    user.groups.add(student_group)

    return user, created


def _synchronize_user_fields(
    user: User,
    identity: GoogleIdentity,
) -> list[str]:
    updated_fields: list[str] = []

    if user.google_subject is None:
        user.google_subject = identity.subject
        updated_fields.append('google_subject')
    elif user.google_subject != identity.subject:
        raise GoogleIdentityConflict(
            'El usuario pertenece a otra identidad de Google.',
        )

    if user.email != identity.email:
        user.email = identity.email
        updated_fields.append('email')

    optional_fields = {
        'first_name': identity.first_name,
        'last_name': identity.last_name,
        'avatar_url': identity.avatar_url,
    }

    for field_name, value in optional_fields.items():
        if not value:
            continue

        if getattr(user, field_name) == value:
            continue

        setattr(
            user,
            field_name,
            value,
        )
        updated_fields.append(field_name)

    return updated_fields
