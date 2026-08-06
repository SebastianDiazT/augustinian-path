from uuid import uuid4

from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import (
    AcademicPeriod,
    Course,
    CourseOffering,
    Faculty,
    ProfessionalSchool,
)
from apps.accounts.models import (
    AcademicAdminAssignment,
    User,
)
from apps.accounts.roles import Role


class CourseOfferingAdminEndpointTests(APITestCase):
    endpoint = '/api/v1/admin/course-offerings/'

    def setUp(self) -> None:
        platform_admin_group = Group.objects.get(
            name=Role.PLATFORM_ADMIN.value,
        )
        academic_admin_group = Group.objects.get(
            name=Role.ACADEMIC_ADMIN.value,
        )
        student_group = Group.objects.get(
            name=Role.STUDENT.value,
        )

        self.platform_admin = User.objects.create_user(
            email='platform.offerings@unsa.edu.pe',
            password='Prueba123!',
        )
        self.platform_admin.groups.add(
            platform_admin_group,
        )

        self.academic_admin = User.objects.create_user(
            email='academic.offerings@unsa.edu.pe',
            password='Prueba123!',
        )
        self.academic_admin.groups.add(
            academic_admin_group,
        )

        self.unassigned_admin = User.objects.create_user(
            email='unassigned.offerings@unsa.edu.pe',
            password='Prueba123!',
        )
        self.unassigned_admin.groups.add(
            academic_admin_group,
        )

        self.student = User.objects.create_user(
            email='student.offerings@unsa.edu.pe',
            password='Prueba123!',
        )
        self.student.groups.add(
            student_group,
        )

        faculty = Faculty.objects.create(
            name='Facultad de Ingeniería',
        )
        self.systems = ProfessionalSchool.objects.create(
            faculty=faculty,
            name='Ingeniería de Sistemas',
        )
        self.industrial = ProfessionalSchool.objects.create(
            faculty=faculty,
            name='Ingeniería Industrial',
        )

        AcademicAdminAssignment.objects.create(
            user=self.academic_admin,
            professional_school=self.systems,
        )

        self.period_a = AcademicPeriod.objects.create(
            year=2026,
            term=AcademicPeriod.Term.FIRST,
        )
        self.period_b = AcademicPeriod.objects.create(
            year=2026,
            term=AcademicPeriod.Term.SECOND,
        )

        self.programming = Course.objects.create(
            professional_school=self.systems,
            code='CS 101',
            name='Programación',
        )
        self.databases = Course.objects.create(
            professional_school=self.systems,
            code='CS 201',
            name='Bases de Datos',
        )
        self.industrial_course = Course.objects.create(
            professional_school=self.industrial,
            code='IN 101',
            name='Introducción a Ingeniería Industrial',
        )

        self.systems_offering = CourseOffering.objects.create(
            academic_period=self.period_a,
            course=self.programming,
            group_code='A',
        )
        self.industrial_offering = CourseOffering.objects.create(
            academic_period=self.period_a,
            course=self.industrial_course,
            group_code='A',
        )

    def detail_endpoint(
        self,
        offering: CourseOffering,
    ) -> str:
        return f'{self.endpoint}{offering.public_id}/'

    def authenticate_academic_admin(self) -> None:
        self.client.force_authenticate(
            user=self.academic_admin,
        )

    def valid_payload(self) -> dict[str, object]:
        return {
            'academic_period_id': str(
                self.period_a.public_id,
            ),
            'course_id': str(
                self.databases.public_id,
            ),
            'group_code': 'B',
        }

    def test_rejects_unauthenticated_list(self) -> None:
        response = self.client.get(
            self.endpoint,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_rejects_student_list(self) -> None:
        self.client.force_authenticate(
            user=self.student,
        )

        response = self.client.get(
            self.endpoint,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_rejects_unassigned_academic_admin(
        self,
    ) -> None:
        self.client.force_authenticate(
            user=self.unassigned_admin,
        )

        response = self.client.get(
            self.endpoint,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_platform_admin_lists_all_offerings(
        self,
    ) -> None:
        self.client.force_authenticate(
            user=self.platform_admin,
        )

        response = self.client.get(
            self.endpoint,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            {
                offering['id']
                for offering in response.json()['data']['course_offerings']
            },
            {
                str(self.systems_offering.public_id),
                str(self.industrial_offering.public_id),
            },
        )

    def test_academic_admin_lists_only_assigned_school(
        self,
    ) -> None:
        self.authenticate_academic_admin()

        response = self.client.get(
            self.endpoint,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [
                offering['id']
                for offering in response.json()['data']['course_offerings']
            ],
            [
                str(self.systems_offering.public_id),
            ],
        )

    def test_filtering_another_school_returns_empty(
        self,
    ) -> None:
        self.authenticate_academic_admin()

        response = self.client.get(
            f'{self.endpoint}?professional_school={self.industrial.public_id}'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.json()['data']['course_offerings'],
            [],
        )

    def test_filters_by_period_and_group(self) -> None:
        self.client.force_authenticate(
            user=self.platform_admin,
        )

        response = self.client.get(
            f'{self.endpoint}?academic_period={self.period_a.public_id}&group_code=A'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            len(response.json()['data']['course_offerings']),
            2,
        )

    def test_academic_admin_creates_assigned_school_offering(
        self,
    ) -> None:
        self.authenticate_academic_admin()

        payload = self.valid_payload()
        payload['group_code'] = '  b  '

        response = self.client.post(
            self.endpoint,
            payload,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.json()['data']['group_code'],
            'B',
        )
        self.assertTrue(
            CourseOffering.objects.filter(
                academic_period=self.period_a,
                course=self.databases,
                group_code='B',
            ).exists()
        )

    def test_academic_admin_cannot_create_for_other_school(
        self,
    ) -> None:
        self.authenticate_academic_admin()

        response = self.client.post(
            self.endpoint,
            {
                'academic_period_id': str(
                    self.period_a.public_id,
                ),
                'course_id': str(
                    self.industrial_course.public_id,
                ),
                'group_code': 'B',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'course_id',
            response.json()['error']['errors'],
        )

    def test_platform_admin_creates_for_any_school(
        self,
    ) -> None:
        self.client.force_authenticate(
            user=self.platform_admin,
        )

        response = self.client.post(
            self.endpoint,
            {
                'academic_period_id': str(
                    self.period_a.public_id,
                ),
                'course_id': str(
                    self.industrial_course.public_id,
                ),
                'group_code': 'B',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_rejects_duplicate_group(self) -> None:
        self.authenticate_academic_admin()

        response = self.client.post(
            self.endpoint,
            {
                'academic_period_id': str(
                    self.period_a.public_id,
                ),
                'course_id': str(
                    self.programming.public_id,
                ),
                'group_code': 'a',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'group_code',
            response.json()['error']['errors'],
        )

    def test_updates_assigned_school_offering(
        self,
    ) -> None:
        self.authenticate_academic_admin()

        response = self.client.patch(
            self.detail_endpoint(
                self.systems_offering,
            ),
            {
                'group_code': 'C',
                'is_active': False,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.systems_offering.refresh_from_db()

        self.assertEqual(
            self.systems_offering.group_code,
            'C',
        )
        self.assertFalse(
            self.systems_offering.is_active,
        )

    def test_rejects_changing_offering_identity(
        self,
    ) -> None:
        self.authenticate_academic_admin()

        response = self.client.patch(
            self.detail_endpoint(
                self.systems_offering,
            ),
            {
                'academic_period_id': str(
                    self.period_b.public_id,
                ),
                'course_id': str(
                    self.databases.public_id,
                ),
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'academic_period_id',
            response.json()['error']['errors'],
        )
        self.assertIn(
            'course_id',
            response.json()['error']['errors'],
        )

    def test_hides_offering_from_another_school(
        self,
    ) -> None:
        self.authenticate_academic_admin()

        response = self.client.patch(
            self.detail_endpoint(
                self.industrial_offering,
            ),
            {
                'group_code': 'C',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.industrial_offering.refresh_from_db()

        self.assertEqual(
            self.industrial_offering.group_code,
            'A',
        )

    def test_rejects_unknown_period_or_course(
        self,
    ) -> None:
        self.authenticate_academic_admin()

        response = self.client.post(
            self.endpoint,
            {
                'academic_period_id': str(uuid4()),
                'course_id': str(uuid4()),
                'group_code': 'B',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'academic_period_id',
            response.json()['error']['errors'],
        )
        self.assertIn(
            'course_id',
            response.json()['error']['errors'],
        )
