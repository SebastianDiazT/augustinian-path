import pytest

from apps.accounts.models import (
    MembershipRequest,
    SchoolDelegation,
    SchoolMembership,
    StudentProfile,
    User,
)
from apps.accounts.serializers import MembershipRequestSerializer, SchoolDelegationSerializer

pytestmark = pytest.mark.django_db


class TestAccountsSerializers:
    @pytest.fixture
    def setup_data(self):
        from apps.curricula.models import CurriculumPlan
        from apps.institution.models import Area, Faculty, ProfessionalSchool

        area = Area.objects.create(name='Ingenierías')
        faculty = Faculty.objects.create(area=area, name='Ingeniería de Producción')
        school = ProfessionalSchool.objects.create(faculty=faculty, name='Sistemas')
        plan = CurriculumPlan.objects.create(school=school, year='2025')
        return school, plan


    def test_delegation_serializer_blocks_duplicates(self, setup_data):
        school, _ = setup_data
        admin = User.objects.create_user(email='admin@unsa.edu.pe')
        delegate = User.objects.create_user(email='del@unsa.edu.pe')

        SchoolDelegation.objects.create(delegate=delegate, school=school, assigned_by=admin)

        data = {'delegate': str(delegate.public_id), 'school': str(school.public_id)}
        serializer = SchoolDelegationSerializer(data=data)

        assert serializer.is_valid() is False
        assert 'non_field_errors' in serializer.errors

    def test_membership_request_serializer_blocks_spam(self, setup_data):
        school, plan = setup_data
        student_user = User.objects.create_user(email='spam@unsa.edu.pe')
        profile = StudentProfile.objects.create(user=student_user, cui='2020999')

        from unittest.mock import Mock

        mock_request = Mock()
        mock_request.user = student_user

        admin = User.objects.create_superuser(email='admin2@unsa.edu.pe')
        from django.utils import timezone

        SchoolMembership.objects.create(
            student=profile,
            school=school,
            curriculum_plan=plan,
            verified_by=admin,
            verified_at=timezone.now(),
        )

        data = {
            'school': str(school.public_id),
            'curriculum_plan': str(plan.public_id),
            'request_type': 'initial_request',
        }
        serializer = MembershipRequestSerializer(data=data, context={'request': mock_request})
        assert serializer.is_valid() is False
        assert 'membresía activa' in str(serializer.errors)

        SchoolMembership.objects.all().delete()
        MembershipRequest.objects.create(
            student=profile, school=school, curriculum_plan=plan, request_type='initial_request'
        )

        serializer2 = MembershipRequestSerializer(data=data, context={'request': mock_request})
        assert serializer2.is_valid() is False
        assert 'pendiente de revisión' in str(serializer2.errors)
