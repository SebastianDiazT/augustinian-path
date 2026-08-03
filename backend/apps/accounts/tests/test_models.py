from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

User = get_user_model()


class UserManagerTests(TestCase):
    def test_create_user_normalizes_email_and_hashes_password(self) -> None:
        user = User.objects.create_user(
            email='USUARIO.PRUEBA@UNSA.EDU.PE',
            password='Prueba123!',
        )

        self.assertEqual(user.email, 'usuario.prueba@unsa.edu.pe')
        self.assertTrue(user.check_password('Prueba123!'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_rejects_non_institutional_email(self) -> None:
        with self.assertRaises(ValidationError):
            User.objects.create_user(
                email='persona@gmail.com',
                password='Prueba123!',
            )

        self.assertFalse(User.objects.filter(email='persona@gmail.com').exists())

    def test_create_superuser_assigns_permissions(self) -> None:
        user = User.objects.create_superuser(
            email='admin@unsa.edu.pe',
            password='Prueba123!',
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
