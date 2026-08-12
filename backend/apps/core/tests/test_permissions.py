from unittest.mock import Mock

from apps.core.permissions import (
    IsOwnerStudent,
    IsPlatformAdmin,
    IsSchoolDelegate,
    student_has_verified_membership,
)


def test_is_platform_admin():
    perm = IsPlatformAdmin()
    req = Mock(user=Mock(is_authenticated=True, is_platform_admin=True))
    assert perm.has_permission(req, None) is True

    req.user.is_platform_admin = False
    assert perm.has_permission(req, None) is False


def test_is_school_delegate():
    perm = IsSchoolDelegate()
    req = Mock(user=Mock(is_authenticated=True))
    req.user.is_delegate_of.return_value = True

    class ObjMethod:
        def get_school(self):
            return 'SchoolA'

    assert perm.has_object_permission(req, None, ObjMethod()) is True
    req.user.is_delegate_of.assert_called_with('SchoolA')

    class ObjAttr:
        school = 'SchoolB'

    assert perm.has_object_permission(req, None, ObjAttr()) is True
    req.user.is_delegate_of.assert_called_with('SchoolB')

    assert perm.has_object_permission(req, None, object()) is False


def test_is_owner_student():
    perm = IsOwnerStudent()
    req = Mock(user=Mock(is_authenticated=True, id=10))

    class ObjStudent:
        student = Mock(user_id=10)

    assert perm.has_object_permission(req, None, ObjStudent()) is True

    ObjStudent.student.user_id = 99
    assert perm.has_object_permission(req, None, ObjStudent()) is False
    assert perm.has_object_permission(req, None, object()) is False


def test_student_has_verified_membership():
    user = Mock()
    del user.student_profile
    assert student_has_verified_membership(user, 'School') is False

    user.student_profile = Mock()
    user.student_profile.memberships.filter.return_value.exists.return_value = True
    assert student_has_verified_membership(user, 'School') is True


def test_permissions_reject_unauthenticated_users():
    req_unauth = Mock(user=Mock(is_authenticated=False))
    req_no_user = Mock(user=None)

    assert IsSchoolDelegate().has_permission(req_unauth, None) is False
    assert IsOwnerStudent().has_permission(req_unauth, None) is False

    # También validamos si el objeto user es None por completo
    assert IsSchoolDelegate().has_permission(req_no_user, None) is False
    assert IsOwnerStudent().has_permission(req_no_user, None) is False