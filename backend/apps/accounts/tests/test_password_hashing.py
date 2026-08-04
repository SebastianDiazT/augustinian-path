from django.contrib.auth.hashers import (
    identify_hasher,
    make_password,
)
from django.test import TestCase

from apps.accounts.models import User


class PasswordHashingTests(TestCase):
    password = 'UnaClaveSegura123!'

    def test_new_passwords_use_argon2(self) -> None:
        user = User.objects.create_user(
            email='argon2@unsa.edu.pe',
            password=self.password,
        )

        hasher = identify_hasher(user.password)

        self.assertEqual(
            hasher.algorithm,
            'argon2',
        )

    def test_upgrades_existing_pbkdf2_password(
        self,
    ) -> None:
        user = User.objects.create(
            email='pbkdf2@unsa.edu.pe',
            password=make_password(
                self.password,
                hasher='pbkdf2_sha256',
            ),
        )

        self.assertEqual(
            identify_hasher(user.password).algorithm,
            'pbkdf2_sha256',
        )
        self.assertTrue(
            user.check_password(self.password),
        )

        user.refresh_from_db()

        self.assertEqual(
            identify_hasher(user.password).algorithm,
            'argon2',
        )
