from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User

pytestmark = pytest.mark.django_db


class TestGoogleAuthAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @patch('apps.accounts.auth_views.google_id_token.verify_oauth2_token')
    def test_login_with_valid_domain_creates_user(self, mock_verify, api_client):
        mock_verify.return_value = {
            'sub': 'google-123',
            'email': 'ana@unsa.edu.pe',
            'email_verified': True,
            'name': 'Ana Pérez',
        }
        res = api_client.post(reverse('accounts:auth-google'), {'id_token': 'fake'})
        assert res.status_code == 200
        assert User.objects.filter(email='ana@unsa.edu.pe').exists()

    @patch('apps.accounts.auth_views.google_id_token.verify_oauth2_token')
    def test_login_updates_existing_admin(self, mock_verify, api_client):
        User.objects.create_superuser(email='admin@unsa.edu.pe', full_name='Admin')
        mock_verify.return_value = {
            'sub': 'sub-admin',
            'email': 'admin@unsa.edu.pe',
            'email_verified': True,
            'name': 'Admin',
        }
        api_client.post(reverse('accounts:auth-google'), {'id_token': 'fake'})
        assert User.objects.get(email='admin@unsa.edu.pe').google_sub == 'sub-admin'

    @patch('apps.accounts.auth_views.google_id_token.verify_oauth2_token')
    def test_login_prevents_account_hijacking(self, mock_verify, api_client):
        User.objects.create_user(email='ana@unsa.edu.pe', google_sub='sub-original')
        mock_verify.return_value = {
            'sub': 'sub-hacker',
            'email': 'ana@unsa.edu.pe',
            'email_verified': True,
        }
        res = api_client.post(reverse('accounts:auth-google'), {'id_token': 'fake'})
        assert res.status_code == 403

    @patch('apps.accounts.auth_views.google_id_token.verify_oauth2_token')
    def test_login_with_invalid_domain_is_rejected(self, mock_verify, api_client):
        mock_verify.return_value = {
            'sub': '456',
            'email': 'ana@gmail.com',
            'email_verified': True,
        }
        res = api_client.post(reverse('accounts:auth-google'), {'id_token': 'fake'})
        assert res.status_code == 403

    @patch('apps.accounts.auth_views.google_id_token.verify_oauth2_token')
    def test_login_with_unverified_email_is_rejected(self, mock_verify, api_client):
        mock_verify.return_value = {
            'sub': '789',
            'email': 'ana@unsa.edu.pe',
            'email_verified': False,
        }
        res = api_client.post(reverse('accounts:auth-google'), {'id_token': 'fake'})
        assert res.status_code == 403

    def test_login_without_id_token_is_rejected(self, api_client):
        res = api_client.post(reverse('accounts:auth-google'), {})
        assert res.status_code == 403

    @patch('apps.accounts.auth_views.google_id_token.verify_oauth2_token')
    def test_login_handles_google_verification_error(self, mock_verify, api_client):
        mock_verify.side_effect = ValueError('Expirado')
        res = api_client.post(reverse('accounts:auth-google'), {'id_token': 'basura'})
        assert res.status_code == 403

    @patch('apps.accounts.auth_views.google_id_token.verify_oauth2_token')
    def test_login_syncs_changed_email_and_name(self, mock_verify, api_client):
        User.objects.create_user(
            email='nuevo@unsa.edu.pe', full_name='Nombre Viejo', google_sub='111'
        )

        mock_verify.return_value = {
            'sub': '111',
            'email': 'nuevo@unsa.edu.pe',
            'email_verified': True,
            'name': 'Nombre Nuevo',
        }

        api_client.post(reverse('accounts:auth-google'), {'id_token': 'fake'})

        user = User.objects.get(google_sub='111')
        assert user.full_name == 'Nombre Nuevo'

    @patch('apps.accounts.auth_views.google_id_token.verify_oauth2_token')
    def test_login_rejected_for_inactive_account(self, mock_verify, api_client):
        User.objects.create_user(email='inactivo@unsa.edu.pe', google_sub='123', is_active=False)

        mock_verify.return_value = {
            'sub': '123',
            'email': 'inactivo@unsa.edu.pe',
            'email_verified': True,
        }
        res = api_client.post(reverse('accounts:auth-google'), {'id_token': 'fake'})
        assert res.status_code == 403
        assert 'desactivada' in str(res.data)

    @patch('apps.accounts.auth_views.google_id_token.verify_oauth2_token')
    def test_login_admin_hijacking_fallback(self, mock_verify, api_client):
        User.objects.create_superuser(email='admin_viejo@unsa.edu.pe', google_sub='sub-original')

        mock_verify.return_value = {
            'sub': 'sub-nuevo-hacker',
            'email': 'admin_viejo@unsa.edu.pe',
            'email_verified': True,
        }
        res = api_client.post(reverse('accounts:auth-google'), {'id_token': 'fake'})
        assert res.status_code == 403