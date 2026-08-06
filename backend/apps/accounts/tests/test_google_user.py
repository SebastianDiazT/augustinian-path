from django.contrib.auth.models import Group
from django.test import TestCase

from apps.accounts.google_identity import GoogleIdentity
from apps.accounts.google_user import (
    GoogleIdentityConflict,
    synchronize_google_user,
)
from apps.accounts.models import User
from apps.accounts.roles import Role


class SynchronizeGoogleUserTests(TestCase):
    def test_creates_user_with_student_role(self) -> None:
        identity = self._identity()

        user, created = synchronize_google_user(
            identity,
        )

        self.assertTrue(created)
        self.assertEqual(
            user.google_subject,
            identity.subject,
        )
        self.assertEqual(
            user.email,
            identity.email,
        )
        self.assertEqual(
            user.first_name,
            identity.first_name,
        )
        self.assertEqual(
            user.last_name,
            identity.last_name,
        )
        self.assertEqual(
            user.avatar_url,
            identity.avatar_url,
        )
        self.assertFalse(
            user.has_usable_password(),
        )
        self.assertTrue(
            user.groups.filter(
                name=Role.STUDENT.value,
            ).exists()
        )

    def test_updates_user_found_by_google_subject(
        self,
    ) -> None:
        user = User.objects.create_user(
            email='correo-anterior@unsa.edu.pe',
            password=None,
            google_subject='google-subject-123',
            first_name='Nombre anterior',
            last_name='Apellido anterior',
            avatar_url='',
        )

        platform_group = Group.objects.get(
            name=Role.PLATFORM_ADMIN.value,
        )
        user.groups.add(platform_group)

        identity = self._identity()

        synchronized_user, created = synchronize_google_user(
            identity,
        )

        self.assertFalse(created)
        self.assertEqual(
            synchronized_user.pk,
            user.pk,
        )

        synchronized_user.refresh_from_db()

        self.assertEqual(
            synchronized_user.email,
            identity.email,
        )
        self.assertEqual(
            synchronized_user.first_name,
            identity.first_name,
        )
        self.assertEqual(
            synchronized_user.last_name,
            identity.last_name,
        )
        self.assertEqual(
            synchronized_user.avatar_url,
            identity.avatar_url,
        )
        self.assertTrue(
            synchronized_user.groups.filter(
                name=Role.STUDENT.value,
            ).exists()
        )
        self.assertTrue(
            synchronized_user.groups.filter(
                name=Role.PLATFORM_ADMIN.value,
            ).exists()
        )

    def test_links_existing_user_found_by_email(
        self,
    ) -> None:
        user = User.objects.create_user(
            email='estudiante@unsa.edu.pe',
            password=None,
            google_subject=None,
        )

        synchronized_user, created = synchronize_google_user(
            self._identity(),
        )

        self.assertFalse(created)
        self.assertEqual(
            synchronized_user.pk,
            user.pk,
        )

        synchronized_user.refresh_from_db()

        self.assertEqual(
            synchronized_user.google_subject,
            'google-subject-123',
        )
        self.assertEqual(
            User.objects.count(),
            1,
        )

    def test_rejects_subject_and_email_conflict(
        self,
    ) -> None:
        User.objects.create_user(
            email='primer-usuario@unsa.edu.pe',
            password=None,
            google_subject='google-subject-123',
        )
        User.objects.create_user(
            email='estudiante@unsa.edu.pe',
            password=None,
            google_subject='different-google-subject',
        )

        with self.assertRaises(
            GoogleIdentityConflict,
        ):
            synchronize_google_user(
                self._identity(),
            )

    def test_does_not_clear_optional_user_data(
        self,
    ) -> None:
        user = User.objects.create_user(
            email='estudiante@unsa.edu.pe',
            password=None,
            google_subject='google-subject-123',
            first_name='Sebastian',
            last_name='Diaz',
            avatar_url='https://example.com/avatar.png',
        )

        identity = GoogleIdentity(
            subject='google-subject-123',
            email='estudiante@unsa.edu.pe',
            first_name='',
            last_name='',
            avatar_url='',
        )

        synchronize_google_user(identity)

        user.refresh_from_db()

        self.assertEqual(
            user.first_name,
            'Sebastian',
        )
        self.assertEqual(
            user.last_name,
            'Diaz',
        )
        self.assertEqual(
            user.avatar_url,
            'https://example.com/avatar.png',
        )

    @staticmethod
    def _identity() -> GoogleIdentity:
        return GoogleIdentity(
            subject='google-subject-123',
            email='estudiante@unsa.edu.pe',
            first_name='Sebastian',
            last_name='Diaz',
            avatar_url=('https://lh3.googleusercontent.com/a/example-avatar'),
        )
