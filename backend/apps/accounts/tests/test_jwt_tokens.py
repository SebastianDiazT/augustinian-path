from django.test import TestCase
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import (
    AccessToken,
    RefreshToken,
)

from apps.accounts.jwt_tokens import (
    InactiveUser,
    issue_token_pair,
)
from apps.accounts.models import User


class IssueTokenPairTests(TestCase):
    def test_issues_access_and_refresh_tokens(
        self,
    ) -> None:
        user = User.objects.create_user(
            email='estudiante@unsa.edu.pe',
            password=None,
            google_subject='google-subject-123',
        )

        token_pair = issue_token_pair(user)

        access_token = AccessToken(
            token_pair.access,
        )
        refresh_token = RefreshToken(
            token_pair.refresh,
        )

        self.assertEqual(
            access_token['sub'],
            str(user.public_id),
        )
        self.assertEqual(
            refresh_token['sub'],
            str(user.public_id),
        )
        self.assertEqual(
            access_token['token_type'],
            'access',
        )
        self.assertEqual(
            refresh_token['token_type'],
            'refresh',
        )
        self.assertTrue(
            OutstandingToken.objects.filter(
                user=user,
            ).exists()
        )

    def test_rejects_inactive_user(
        self,
    ) -> None:
        user = User.objects.create_user(
            email='desactivado@unsa.edu.pe',
            password=None,
            google_subject='google-subject-inactive',
            is_active=False,
        )

        with self.assertRaises(InactiveUser):
            issue_token_pair(user)

        self.assertFalse(
            OutstandingToken.objects.filter(
                user=user,
            ).exists()
        )
