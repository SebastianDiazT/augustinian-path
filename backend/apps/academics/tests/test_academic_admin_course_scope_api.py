from decimal import Decimal

from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import (
    Course,
    CurriculumCourse,
    CurriculumPlan,
    Faculty,
    ProfessionalSchool,
)
from apps.accounts.models import (
    AcademicAdminAssignment,
    User,
)
from apps.accounts.roles import Role


class AcademicAdminCourseScopeTests(APITestCase):
    course_endpoint = '/api/v1/admin/courses/'
    curriculum_course_endpoint = '/api/v1/admin/curriculum-courses/'

    def setUp(self) -> None:
        academic_admin_group = Group.objects.get(
            name=Role.ACADEMIC_ADMIN.value,
        )

        self.academic_admin = User.objects.create_user(
            email='admin.catalogo@unsa.edu.pe',
            password='Prueba123!',
        )
        self.academic_admin.groups.add(
            academic_admin_group,
        )

        self.unassigned_admin = User.objects.create_user(
            email='admin.catalogo.sin.escuela@unsa.edu.pe',
            password='Prueba123!',
        )
        self.unassigned_admin.groups.add(
            academic_admin_group,
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

        self.systems_plan = CurriculumPlan.objects.create(
            professional_school=self.systems,
            code='2025',
            name='Plan Sistemas 2025',
        )
        self.industrial_plan = CurriculumPlan.objects.create(
            professional_school=self.industrial,
            code='2025',
            name='Plan Industrial 2025',
        )

        self.programming = Course.objects.create(
            professional_school=self.systems,
            code='CS 101',
            name='Programación',
        )
        self.data_structures = Course.objects.create(
            professional_school=self.systems,
            code='CS 201',
            name='Estructuras de Datos',
        )
        self.industrial_course = Course.objects.create(
            professional_school=self.industrial,
            code='IN 101',
            name='Introducción a Ingeniería Industrial',
        )

        self.systems_entry = CurriculumCourse.objects.create(
            curriculum_plan=self.systems_plan,
            course=self.programming,
            cycle=1,
            credits=Decimal('4.00'),
        )
        self.industrial_entry = CurriculumCourse.objects.create(
            curriculum_plan=self.industrial_plan,
            course=self.industrial_course,
            cycle=1,
            credits=Decimal('3.00'),
        )

    def course_detail_endpoint(
        self,
        course: Course,
    ) -> str:
        return f'{self.course_endpoint}{course.public_id}/'

    def curriculum_course_detail_endpoint(
        self,
        entry: CurriculumCourse,
    ) -> str:
        return f'{self.curriculum_course_endpoint}{entry.public_id}/'

    def authenticate_academic_admin(self) -> None:
        self.client.force_authenticate(
            user=self.academic_admin,
        )

    def test_course_endpoint_rejects_unassigned_admin(
        self,
    ) -> None:
        self.client.force_authenticate(
            user=self.unassigned_admin,
        )

        response = self.client.get(
            self.course_endpoint,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_lists_only_courses_from_assigned_school(
        self,
    ) -> None:
        self.authenticate_academic_admin()

        response = self.client.get(
            self.course_endpoint,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            {course['id'] for course in response.json()['data']['courses']},
            {
                str(self.programming.public_id),
                str(self.data_structures.public_id),
            },
        )

    def test_filtering_courses_by_another_school_returns_empty(
        self,
    ) -> None:
        self.authenticate_academic_admin()

        response = self.client.get(
            f'{self.course_endpoint}?professional_school={self.industrial.public_id}'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.json()['data']['courses'],
            [],
        )

    def test_creates_course_in_assigned_school(self) -> None:
        self.authenticate_academic_admin()

        response = self.client.post(
            self.course_endpoint,
            {
                'professional_school_id': str(
                    self.systems.public_id,
                ),
                'code': 'CS 301',
                'name': 'Algoritmos Avanzados',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertTrue(
            Course.objects.filter(
                professional_school=self.systems,
                code='CS 301',
            ).exists()
        )

    def test_rejects_course_creation_in_another_school(
        self,
    ) -> None:
        self.authenticate_academic_admin()

        response = self.client.post(
            self.course_endpoint,
            {
                'professional_school_id': str(
                    self.industrial.public_id,
                ),
                'code': 'IN 201',
                'name': 'Curso industrial',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'professional_school_id',
            response.json()['error']['errors'],
        )

    def test_updates_course_from_assigned_school(self) -> None:
        self.authenticate_academic_admin()

        response = self.client.patch(
            self.course_detail_endpoint(
                self.programming,
            ),
            {
                'name': 'Programación actualizada',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.programming.refresh_from_db()

        self.assertEqual(
            self.programming.name,
            'Programación actualizada',
        )

    def test_hides_course_from_another_school(self) -> None:
        self.authenticate_academic_admin()

        response = self.client.patch(
            self.course_detail_endpoint(
                self.industrial_course,
            ),
            {
                'name': 'Cambio no autorizado',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.industrial_course.refresh_from_db()

        self.assertEqual(
            self.industrial_course.name,
            'Introducción a Ingeniería Industrial',
        )

    def test_curriculum_course_endpoint_rejects_unassigned_admin(
        self,
    ) -> None:
        self.client.force_authenticate(
            user=self.unassigned_admin,
        )

        response = self.client.get(
            self.curriculum_course_endpoint,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_lists_only_curriculum_courses_from_assigned_school(
        self,
    ) -> None:
        self.authenticate_academic_admin()

        response = self.client.get(
            self.curriculum_course_endpoint,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            {entry['id'] for entry in response.json()['data']['curriculum_courses']},
            {
                str(self.systems_entry.public_id),
            },
        )

    def test_filtering_curriculum_courses_by_other_school_is_empty(
        self,
    ) -> None:
        self.authenticate_academic_admin()

        response = self.client.get(
            f'{self.curriculum_course_endpoint}'
            f'?professional_school={self.industrial.public_id}'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.json()['data']['curriculum_courses'],
            [],
        )

    def test_creates_curriculum_course_in_assigned_school(
        self,
    ) -> None:
        self.authenticate_academic_admin()

        response = self.client.post(
            self.curriculum_course_endpoint,
            {
                'curriculum_plan_id': str(
                    self.systems_plan.public_id,
                ),
                'course_id': str(
                    self.data_structures.public_id,
                ),
                'cycle': 2,
                'credits': '4.50',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertTrue(
            CurriculumCourse.objects.filter(
                curriculum_plan=self.systems_plan,
                course=self.data_structures,
            ).exists()
        )

    def test_rejects_curriculum_plan_from_another_school(
        self,
    ) -> None:
        self.authenticate_academic_admin()

        response = self.client.post(
            self.curriculum_course_endpoint,
            {
                'curriculum_plan_id': str(
                    self.industrial_plan.public_id,
                ),
                'course_id': str(
                    self.data_structures.public_id,
                ),
                'cycle': 2,
                'credits': '4.00',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'curriculum_plan_id',
            response.json()['error']['errors'],
        )

    def test_rejects_curriculum_course_from_another_school(
        self,
    ) -> None:
        self.authenticate_academic_admin()

        response = self.client.post(
            self.curriculum_course_endpoint,
            {
                'curriculum_plan_id': str(
                    self.systems_plan.public_id,
                ),
                'course_id': str(
                    self.industrial_course.public_id,
                ),
                'cycle': 2,
                'credits': '4.00',
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

    def test_updates_curriculum_course_from_assigned_school(
        self,
    ) -> None:
        self.authenticate_academic_admin()

        response = self.client.patch(
            self.curriculum_course_detail_endpoint(
                self.systems_entry,
            ),
            {
                'cycle': 2,
                'credits': '4.50',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.systems_entry.refresh_from_db()

        self.assertEqual(
            self.systems_entry.cycle,
            2,
        )
        self.assertEqual(
            self.systems_entry.credits,
            Decimal('4.50'),
        )

    def test_hides_curriculum_course_from_another_school(
        self,
    ) -> None:
        self.authenticate_academic_admin()

        response = self.client.patch(
            self.curriculum_course_detail_endpoint(
                self.industrial_entry,
            ),
            {
                'cycle': 3,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.industrial_entry.refresh_from_db()

        self.assertEqual(
            self.industrial_entry.cycle,
            1,
        )
