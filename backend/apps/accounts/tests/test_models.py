import pytest
from django.db import IntegrityError

from apps.accounts.models import StudentProfile, User

pytestmark = pytest.mark.django_db


class TestAccountsModels:
    def test_create_user_without_password_is_unusable(self):
        user = User.objects.create_user(email='ana@unsa.edu.pe', full_name='Ana Pérez')
        assert user.email == 'ana@unsa.edu.pe'
        assert not user.has_usable_password()
        assert user.is_platform_admin is False
        assert user.is_staff is False

    def test_create_superuser_sets_the_right_flags(self):
        admin = User.objects.create_superuser(email='admin@unsa.edu.pe', password='secure123')
        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.is_platform_admin is True
        assert admin.check_password('secure123')

    def test_user_without_profile_is_not_a_student(self):
        user = User.objects.create_user(email='ana@unsa.edu.pe', full_name='Ana')
        assert user.is_student is False

    def test_user_with_profile_is_a_student(self):
        user = User.objects.create_user(email='ana@unsa.edu.pe', full_name='Ana')
        StudentProfile.objects.create(user=user, cui='20201234')

        reloaded_user = User.objects.get(pk=user.pk)
        assert reloaded_user.is_student is True

    def test_cui_is_unique(self):
        u1 = User.objects.create_user(email='a@unsa.edu.pe', full_name='A')
        u2 = User.objects.create_user(email='b@unsa.edu.pe', full_name='B')
        StudentProfile.objects.create(user=u1, cui='111')

        with pytest.raises(IntegrityError):
            StudentProfile.objects.create(user=u2, cui='111')

    def test_public_id_is_generated_automatically(self):
        user = User.objects.create_user(email='ana@unsa.edu.pe', full_name='Ana')
        assert user.public_id is not None

    def test_user_manager_requires_email(self):
        with pytest.raises(ValueError, match='Email is required'):
            User.objects.create_user(email='')

    def test_superuser_requires_staff_flag(self):
        with pytest.raises(ValueError, match='must have is_staff=True'):
            User.objects.create_superuser(email='admin@unsa.edu.pe', password='123', is_staff=False)

    def test_superuser_requires_superuser_flag(self):
        with pytest.raises(ValueError, match='must have is_superuser=True'):
            User.objects.create_superuser(
                email='admin@unsa.edu.pe', password='123', is_superuser=False
            )

    def test_models_string_representations(self):
        from apps.accounts.models import MembershipRequest, SchoolDelegation, SchoolMembership
        from apps.curricula.models import CurriculumPlan
        from apps.institution.models import Area, Faculty, ProfessionalSchool

        user = User.objects.create_user(email='test@unsa.edu.pe', full_name='Test User')
        assert str(user) == 'test@unsa.edu.pe'

        profile = StudentProfile.objects.create(user=user, cui='2020')
        assert 'test@unsa.edu.pe' in str(profile)

        area = Area.objects.create(name='Test Area')
        faculty = Faculty.objects.create(area=area, name='Test Faculty')
        school = ProfessionalSchool.objects.create(faculty=faculty, name='Test School')
        plan = CurriculumPlan.objects.create(school=school, year='2025')

        membership = SchoolMembership.objects.create(
            student=profile, school=school, curriculum_plan=plan, verified_at='2026-01-01T00:00:00Z'
        )
        assert 'Test School' in str(membership)

        request = MembershipRequest.objects.create(
            student=profile, school=school, curriculum_plan=plan, request_type='initial_request'
        )
        assert 'pending' in str(request)

        delegation = SchoolDelegation.objects.create(delegate=user, school=school)
        assert 'Test School' in str(delegation)

        assert user.is_delegate_of(school) is True