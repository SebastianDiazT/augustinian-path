from unittest.mock import Mock

import pytest

from apps.institution.views import _IsAdminOrDelegateOfThisSchool

pytestmark = pytest.mark.django_db


class TestInstitutionPermissions:
    def test_wrapper_allows_platform_admin_immediately(self):
        permission = _IsAdminOrDelegateOfThisSchool()

        mock_request = Mock()
        mock_request.user.is_platform_admin = True

        has_permission = permission.has_object_permission(mock_request, Mock(), Mock())
        assert has_permission is True

    def test_wrapper_delegates_to_super_if_not_admin(self, mocker):
        permission = _IsAdminOrDelegateOfThisSchool()

        mock_request = Mock()
        mock_request.user.is_platform_admin = False

        mock_super = mocker.patch(
            'apps.core.permissions.IsSchoolDelegate.has_object_permission', return_value=False
        )
        has_permission = permission.has_object_permission(mock_request, Mock(), Mock())

        mock_super.assert_called_once()
        assert has_permission is False
