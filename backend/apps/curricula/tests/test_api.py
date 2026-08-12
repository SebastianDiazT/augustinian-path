import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import SchoolDelegation, User
from apps.curricula.models import AcademicTerm, Course, CurriculumPlan, Syllabus
from apps.institution.models import Area, Faculty, ProfessionalSchool

pytestmark = pytest.mark.django_db


class TestCurriculaAPI:
    @pytest.fixture
    def setup_data(self):
        area = Area.objects.create(name='Area')
        faculty = Faculty.objects.create(area=area, name='Fac')
        school1 = ProfessionalSchool.objects.create(faculty=faculty, name='School1')
        school2 = ProfessionalSchool.objects.create(faculty=faculty, name='School2')

        admin = User.objects.create_superuser(email='admin@u.pe')
        delegate = User.objects.create_user(email='del@u.pe')
        SchoolDelegation.objects.create(delegate=delegate, school=school1, assigned_by=admin)
        student = User.objects.create_user(email='est@u.pe')

        plan1 = CurriculumPlan.objects.create(school=school1, year='2026')
        term = AcademicTerm.objects.create(
            code='2026-A', start_date='2026-01-01', end_date='2026-06-01'
        )
        course = Course.objects.create(
            curriculum_plan=plan1,
            code='C1',
            name='C1',
            credits=3,
            cycle=1,
            course_type='mandatory',
            academic_area='specialty',
        )
        syllabus = Syllabus.objects.create(course=course, academic_term=term)

        return school1, school2, admin, delegate, student, plan1, term, course, syllabus

    def test_read_only_for_authenticated(self, setup_data):
        school1, _, _, _, student, _, _, _, _ = setup_data
        client = APIClient()
        client.force_authenticate(student)

        # Cubre permisos de GET (Líneas sueltas 94 y 105 en views)
        assert (
            client.get(reverse('curricula:curriculum-plan-list')).status_code == status.HTTP_200_OK
        )
        assert client.get(reverse('curricula:instructor-list')).status_code == status.HTTP_200_OK
        assert client.get(reverse('curricula:academic-term-list')).status_code == status.HTTP_200_OK

        assert (
            client.post(
                reverse('curricula:curriculum-plan-list'),
                {'school': str(school1.public_id), 'year': '2099'},
                format='json',
            ).status_code
            == status.HTTP_403_FORBIDDEN
        )

    def test_admin_can_manage_global_and_school_resources(self, setup_data):
        school1, _, admin, _, _, _, _, _, _ = setup_data
        client = APIClient()
        client.force_authenticate(admin)

        client.post(
            reverse('curricula:academic-term-list'),
            {'code': '2026-B', 'start_date': '2026-07-01', 'end_date': '2026-12-01'},
            format='json',
        )

        plan_res = client.post(
            reverse('curricula:curriculum-plan-list'),
            {'school': str(school1.public_id), 'year': '2028'},
            format='json',
        )
        assert plan_res.status_code == status.HTTP_201_CREATED
        plan_id = plan_res.data['public_id']

        url = reverse('curricula:curriculum-plan-detail', kwargs={'public_id': plan_id})
        assert (
            client.put(
                url, {'school': str(school1.public_id), 'year': '2029'}, format='json'
            ).status_code
            == status.HTTP_200_OK
        )

    def test_delegate_can_create_and_edit_in_own_school(self, setup_data):
        school1, school2, _, delegate, _, _, _, _, _ = setup_data
        client = APIClient()
        client.force_authenticate(delegate)

        res = client.post(
            reverse('curricula:curriculum-plan-list'),
            {'school': str(school1.public_id), 'year': '2027'},
            format='json',
        )
        assert res.status_code == status.HTTP_201_CREATED
        plan_id = res.data['public_id']

        url = reverse('curricula:curriculum-plan-detail', kwargs={'public_id': plan_id})
        assert client.patch(url, {'year': '2028'}, format='json').status_code == status.HTTP_200_OK

        res_bad = client.post(
            reverse('curricula:curriculum-plan-list'),
            {'school': str(school2.public_id), 'year': '2099'},
            format='json',
        )
        assert res_bad.status_code == status.HTTP_403_FORBIDDEN

        term_res = client.post(
            reverse('curricula:academic-term-list'),
            {'code': '2026-C', 'start_date': '2026-07-01', 'end_date': '2026-12-01'},
            format='json',
        )
        assert term_res.status_code == status.HTTP_403_FORBIDDEN

    def test_set_evaluation_components(self, setup_data):
        _, _, admin, _, _, _, _, _, syllabus = setup_data
        client = APIClient()
        client.force_authenticate(admin)

        url = reverse(
            'curricula:syllabus-set-evaluation-components', kwargs={'public_id': syllabus.public_id}
        )

        bad_data = [{'name': 'P1', 'weight': '50.00', 'order': 1}]
        assert client.put(url, bad_data, format='json').status_code == status.HTTP_400_BAD_REQUEST

        good_data = [
            {'name': 'P1', 'weight': '50.00', 'order': 1},
            {'name': 'P2', 'weight': '50.00', 'order': 2},
        ]
        assert client.put(url, good_data, format='json').status_code == status.HTTP_200_OK

    def test_other_viewsets_for_coverage(self, setup_data):
        school1, _, admin, _, _, plan1, term, course, _ = setup_data
        client = APIClient()
        client.force_authenticate(admin)

        ins_res = client.post(
            reverse('curricula:instructor-list'), {'full_name': 'Juan'}, format='json'
        )

        client.post(reverse('curricula:instructor-list'), {'full_name': 'Juan'}, format='json')

        client.post(
            reverse('curricula:elective-branch-list'),
            {'curriculum_plan': str(plan1.public_id), 'name': 'Rama 1'},
            format='json',
        )

        c2_res = client.post(
            reverse('curricula:course-list'),
            {
                'curriculum_plan': str(plan1.public_id),
                'code': 'C2',
                'name': 'C2',
                'credits': 3,
                'cycle': 2,
                'course_type': 'mandatory',
                'academic_area': 'specialty',
            },
            format='json',
        )
        assert c2_res.status_code == status.HTTP_201_CREATED

        pre_res = client.post(
            reverse('curricula:prerequisite-list'),
            {'course': str(c2_res.data['public_id']), 'required_course': str(course.public_id)},
            format='json',
        )
        assert pre_res.status_code == status.HTTP_201_CREATED

        syl_res = client.post(
            reverse('curricula:syllabus-list'),
            {
                'course': str(c2_res.data['public_id']),
                'academic_term': str(term.public_id),
                'instructors': [str(ins_res.data['public_id'])],
            },
            format='json',
        )
        assert syl_res.status_code == status.HTTP_201_CREATED

    def test_delete_action_blocks_unauthorized(self, setup_data):
        school1, school2, admin, delegate, _, plan1, _, _, _ = setup_data
        client = APIClient()

        client.force_authenticate(admin)
        url = reverse('curricula:curriculum-plan-detail', kwargs={'public_id': plan1.public_id})
        assert client.delete(url).status_code == status.HTTP_204_NO_CONTENT

        client.force_authenticate(delegate)
        plan2 = CurriculumPlan.objects.create(school=school2, year='2099')
        url2 = reverse('curricula:curriculum-plan-detail', kwargs={'public_id': plan2.public_id})
        assert client.delete(url2).status_code == status.HTTP_403_FORBIDDEN
