import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import (
    MembershipRequest,
    SchoolDelegation,
    SchoolMembership,
    StudentProfile,
    User,
)

pytestmark = pytest.mark.django_db


class TestAccountsAPI:
    @pytest.fixture
    def setup_data(self):
        from apps.curricula.models import CurriculumPlan
        from apps.institution.models import Area, Faculty, ProfessionalSchool

        area = Area.objects.create(name='Ingenierías')
        faculty = Faculty.objects.create(area=area, name='Ingeniería de Producción')
        school = ProfessionalSchool.objects.create(faculty=faculty, name='Sistemas')
        plan = CurriculumPlan.objects.create(school=school, year='2025')
        return school, plan

    def test_student_profile_creation_and_retrieval(self):
        user = User.objects.create_user(email='nuevo@unsa.edu.pe', full_name='Nuevo')
        client = APIClient()
        client.force_authenticate(user)

        assert (
            client.get(reverse('accounts:student-profile-me')).status_code
            == status.HTTP_404_NOT_FOUND
        )
        assert (
            client.post(reverse('accounts:student-profile-me'), {'cui': '20261234'}).status_code
            == status.HTTP_201_CREATED
        )
        assert (
            client.post(reverse('accounts:student-profile-me'), {'cui': '999999'}).status_code
            == status.HTTP_409_CONFLICT
        )
        assert (
            client.patch(reverse('accounts:student-profile-me'), {'cui': '20260000'}).status_code
            == status.HTTP_200_OK
        )
        assert client.get(reverse('accounts:student-profile-me')).status_code == status.HTTP_200_OK

    def test_cannot_patch_profile_if_it_does_not_exist(self):
        user = User.objects.create_user(email='sinperfil@unsa.edu.pe')
        client = APIClient()
        client.force_authenticate(user)
        assert (
            client.patch(reverse('accounts:student-profile-me'), {'cui': '123'}).status_code
            == status.HTTP_404_NOT_FOUND
        )

    def test_standard_student_profile_creation(self):
        user = User.objects.create_user(email='std@unsa.edu.pe')
        client = APIClient()
        client.force_authenticate(user)
        assert (
            client.post(reverse('accounts:student-profile-list'), {'cui': '12345'}).status_code
            == status.HTTP_201_CREATED
        )

    def test_non_student_non_admin_listing_memberships(self):
        user = User.objects.create_user(email='ghost@unsa.edu.pe')
        client = APIClient()
        client.force_authenticate(user)
        res = client.get(reverse('accounts:school-membership-list'))
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data['data']) == 0

    def test_student_can_list_own_memberships(self, setup_data):
        school, plan = setup_data
        student_user = User.objects.create_user(email='est@unsa.edu.pe')
        profile = StudentProfile.objects.create(user=student_user, cui='2020')
        admin = User.objects.create_superuser(email='admin@unsa.edu.pe')
        SchoolMembership.objects.create(
            student=profile,
            school=school,
            curriculum_plan=plan,
            verified_by=admin,
            verified_at=timezone.now(),
        )

        client = APIClient()
        client.force_authenticate(student_user)
        res = client.get(reverse('accounts:school-membership-list'))
        assert len(res.data['data']) == 1

    def test_student_cannot_approve_own_request(self, setup_data):
        school, plan = setup_data
        student_user = User.objects.create_user(email='est2@unsa.edu.pe')
        profile = StudentProfile.objects.create(user=student_user, cui='2021')
        req = MembershipRequest.objects.create(
            student=profile, school=school, curriculum_plan=plan, request_type='initial_request'
        )

        client = APIClient()
        client.force_authenticate(student_user)
        res = client.post(
            reverse('accounts:membership-request-approve', args=[req.public_id]),
            {'resolution_comment': ''},
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_delegate_cannot_resolve_other_school(self, setup_data):
        school, plan = setup_data
        delegate = User.objects.create_user(email='del@unsa.edu.pe')
        student_user = User.objects.create_user(email='est@unsa.edu.pe')
        profile = StudentProfile.objects.create(user=student_user, cui='2020')
        req = MembershipRequest.objects.create(
            student=profile, school=school, curriculum_plan=plan, request_type='initial_request'
        )

        client = APIClient()
        client.force_authenticate(delegate)
        res = client.post(
            reverse('accounts:membership-request-approve', args=[req.public_id]),
            {'resolution_comment': ''},
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_api_conflict_error_on_already_resolved_request(self, setup_data):
        school, plan = setup_data
        admin = User.objects.create_superuser(email='admin@unsa.edu.pe')
        student_user = User.objects.create_user(email='est3@unsa.edu.pe')
        profile = StudentProfile.objects.create(user=student_user, cui='2022')
        req = MembershipRequest.objects.create(
            student=profile,
            school=school,
            curriculum_plan=plan,
            request_type='initial_request',
            status='approved',
        )

        client = APIClient()
        client.force_authenticate(admin)
        res = client.post(
            reverse('accounts:membership-request-approve', args=[req.public_id]),
            {'resolution_comment': ''},
        )
        assert res.status_code == status.HTTP_409_CONFLICT

    def test_simultaneous_double_resolution_only_updates_once(self, setup_data):
        school, plan = setup_data
        student_user = User.objects.create_user(email='studentx@unsa.edu.pe')
        profile = StudentProfile.objects.create(user=student_user, cui='2020002')
        request = MembershipRequest.objects.create(
            student=profile, school=school, curriculum_plan=plan, request_type='initial_request'
        )

        first = MembershipRequest.objects.filter(pk=request.pk, status='pending').update(
            status='approved'
        )
        second = MembershipRequest.objects.filter(pk=request.pk, status='pending').update(
            status='rejected'
        )

        assert first == 1
        assert second == 0

    def test_resolve_membership_requests_via_api(self, setup_data):
        school, plan = setup_data
        admin = User.objects.create_superuser(email='admin@unsa.edu.pe')
        student_user = User.objects.create_user(email='est4@unsa.edu.pe')
        profile = StudentProfile.objects.create(user=student_user, cui='2020')
        req_app = MembershipRequest.objects.create(
            student=profile, school=school, curriculum_plan=plan, request_type='initial_request'
        )
        req_rej = MembershipRequest.objects.create(
            student=profile, school=school, curriculum_plan=plan, request_type='add_second_program'
        )

        client = APIClient()
        client.force_authenticate(admin)
        assert (
            client.post(
                reverse('accounts:membership-request-approve', args=[req_app.public_id]),
                {'resolution_comment': 'Ok'},
            ).status_code
            == status.HTTP_200_OK
        )
        assert (
            client.post(
                reverse('accounts:membership-request-reject', args=[req_rej.public_id]),
                {'resolution_comment': 'No'},
            ).status_code
            == status.HTTP_200_OK
        )

    def test_cannot_request_membership_without_profile(self, setup_data):
        school, plan = setup_data
        user_no_profile = User.objects.create_user(email='nada@unsa.edu.pe')
        client = APIClient()
        client.force_authenticate(user_no_profile)
        payload = {
            'school': str(school.public_id),
            'curriculum_plan': str(plan.public_id),
            'request_type': 'initial_request',
        }
        assert (
            client.post(reverse('accounts:membership-request-list'), payload).status_code
            == status.HTTP_400_BAD_REQUEST
        )

    def test_student_can_create_and_list_membership_request(self, setup_data):
        school, plan = setup_data
        student_user = User.objects.create_user(email='est5@unsa.edu.pe')
        StudentProfile.objects.create(user=student_user, cui='2020123')
        client = APIClient()
        client.force_authenticate(student_user)

        payload = {
            'school': str(school.public_id),
            'curriculum_plan': str(plan.public_id),
            'request_type': 'initial_request',
        }
        assert (
            client.post(reverse('accounts:membership-request-list'), payload).status_code
            == status.HTTP_201_CREATED
        )
        assert len(client.get(reverse('accounts:membership-request-list')).data['data']) == 1

    def test_delegate_can_list_only_delegated_requests(self, setup_data):
        school, plan = setup_data
        admin = User.objects.create_superuser(email='admin@unsa.edu.pe')
        delegate = User.objects.create_user(email='del2@unsa.edu.pe')
        SchoolDelegation.objects.create(delegate=delegate, school=school, assigned_by=admin)

        client = APIClient()
        client.force_authenticate(delegate)
        assert (
            client.get(reverse('accounts:membership-request-list')).status_code
            == status.HTTP_200_OK
        )

    def test_non_admin_cannot_create_delegation(self, setup_data):
        school, _ = setup_data
        delegate = User.objects.create_user(email='del3@unsa.edu.pe')
        client = APIClient()
        client.force_authenticate(delegate)
        res = client.post(
            reverse('accounts:school-delegation-list'),
            {'delegate': str(delegate.public_id), 'school': str(school.public_id)},
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_delegate_can_list_own_delegations(self, setup_data):
        school, _ = setup_data
        admin = User.objects.create_superuser(email='admin@unsa.edu.pe')
        delegate = User.objects.create_user(email='del4@unsa.edu.pe')
        SchoolDelegation.objects.create(delegate=delegate, school=school, assigned_by=admin)

        client = APIClient()
        client.force_authenticate(delegate)
        res = client.get(reverse('accounts:school-delegation-list'))
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data['data']) == 1

    def test_admin_can_list_all_memberships_and_requests(self):
        client = APIClient()
        admin = User.objects.create_superuser(email='admin_all@unsa.edu.pe')
        client.force_authenticate(admin)
        assert (
            client.get(reverse('accounts:membership-request-list')).status_code
            == status.HTTP_200_OK
        )
        assert (
            client.get(reverse('accounts:school-membership-list')).status_code == status.HTTP_200_OK
        )
        assert (
            client.get(reverse('accounts:school-delegation-list')).status_code == status.HTTP_200_OK
        )

    def test_admin_can_create_delegation(self, setup_data):
        school, _ = setup_data
        admin = User.objects.create_superuser(email='admin2@unsa.edu.pe')
        delegate = User.objects.create_user(email='del5@unsa.edu.pe')
        client = APIClient()
        client.force_authenticate(admin)
        payload = {'delegate': str(delegate.public_id), 'school': str(school.public_id)}
        assert (
            client.post(reverse('accounts:school-delegation-list'), payload).status_code
            == status.HTTP_201_CREATED
        )

    def test_school_delegation_soft_delete(self, setup_data):
        school, _ = setup_data
        admin = User.objects.create_superuser(email='admin3@unsa.edu.pe')
        delegate = User.objects.create_user(email='del6@unsa.edu.pe')
        delegation = SchoolDelegation.objects.create(
            delegate=delegate, school=school, assigned_by=admin
        )

        client = APIClient()
        client.force_authenticate(admin)
        assert (
            client.delete(
                reverse('accounts:school-delegation-detail', args=[delegation.public_id])
            ).status_code
            == status.HTTP_204_NO_CONTENT
        )
        delegation.refresh_from_db()
        assert delegation.is_active is False

    def test_me_endpoint_not_found_and_conflict(self):
        client = APIClient()

        user_empty = User.objects.create_user(email='empty@unsa.edu.pe')
        client.force_authenticate(user_empty)
        assert (
            client.get(reverse('accounts:student-profile-me')).status_code
            == status.HTTP_404_NOT_FOUND
        )

        user_full = User.objects.create_user(email='full@unsa.edu.pe')
        StudentProfile.objects.create(user=user_full, cui='9999')
        client.force_authenticate(user_full)
        assert (
            client.post(reverse('accounts:student-profile-me'), {'cui': '8888'}).status_code
            == status.HTTP_409_CONFLICT
        )