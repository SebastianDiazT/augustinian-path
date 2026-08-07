from decimal import Decimal
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
from apps.accounts.models import User
from apps.accounts.roles import Role
from apps.grading.models import EvaluationComponent, EvaluationScheme


class GradeSimulationApiTests(APITestCase):
    def setUp(self) -> None:
        self.student = User.objects.create_user(
            email='student.grading@unsa.edu.pe',
            password='Prueba123!',
        )
        self.student.groups.add(
            Group.objects.get(name=Role.STUDENT.value),
        )
        faculty = Faculty.objects.create(
            name='Facultad de Ingeniería',
        )
        school = ProfessionalSchool.objects.create(
            faculty=faculty,
            name='Ingeniería de Sistemas',
        )
        course = Course.objects.create(
            professional_school=school,
            code='CS 101',
            name='Programación',
        )
        period = AcademicPeriod.objects.create(
            year=2026,
            term=AcademicPeriod.Term.FIRST,
        )
        offering = CourseOffering.objects.create(
            academic_period=period,
            course=course,
        )
        self.scheme = EvaluationScheme.objects.create(
            course_offering=offering,
        )
        self.exam_1 = EvaluationComponent.objects.create(
            scheme=self.scheme,
            name='Examen 1',
            component_type=EvaluationComponent.ComponentType.EXAM_1,
            weight=Decimal('30.00'),
            order=1,
        )
        self.exam_2 = EvaluationComponent.objects.create(
            scheme=self.scheme,
            name='Examen 2',
            component_type=EvaluationComponent.ComponentType.EXAM_2,
            weight=Decimal('30.00'),
            order=2,
        )
        self.continuous = EvaluationComponent.objects.create(
            scheme=self.scheme,
            name='Evaluación continua',
            component_type=EvaluationComponent.ComponentType.OTHER,
            weight=Decimal('40.00'),
            order=3,
        )
        self.substitute = EvaluationComponent.objects.create(
            scheme=self.scheme,
            name='Sustitutorio',
            component_type=EvaluationComponent.ComponentType.SUBSTITUTE,
            weight=Decimal('0.00'),
            order=4,
        )
        self.endpoint = f'/api/v1/grading/schemes/{self.scheme.public_id}/simulate/'

    def authenticate(self) -> None:
        self.client.force_authenticate(user=self.student)

    def test_rejects_unauthenticated_simulation(self) -> None:
        response = self.client.post(
            self.endpoint,
            {},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simulates_pending_components_without_persisting(self) -> None:
        self.authenticate()
        schemes_before = EvaluationScheme.objects.count()
        components_before = EvaluationComponent.objects.count()

        response = self.client.post(
            self.endpoint,
            {
                'grades': [
                    {
                        'component_id': str(self.continuous.public_id),
                        'score': '15.00',
                    },
                ],
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()['data']
        self.assertEqual(data['final_average'], '6.00')
        self.assertEqual(data['points_missing'], '4.50')
        self.assertEqual(data['used_percentage'], '40.00')
        self.assertEqual(data['remaining_percentage'], '60.00')
        self.assertEqual(len(data['pending_components']), 2)
        self.assertEqual(EvaluationScheme.objects.count(), schemes_before)
        self.assertEqual(EvaluationComponent.objects.count(), components_before)

    def test_applies_substitute_even_when_it_lowers_the_exam(self) -> None:
        self.authenticate()

        response = self.client.post(
            self.endpoint,
            {
                'grades': [
                    {
                        'component_id': str(self.exam_1.public_id),
                        'score': '12.00',
                    },
                    {
                        'component_id': str(self.exam_2.public_id),
                        'score': '16.00',
                    },
                    {
                        'component_id': str(self.continuous.public_id),
                        'score': '10.00',
                    },
                    {
                        'component_id': str(self.substitute.public_id),
                        'score': '5.00',
                    },
                ],
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['data']['final_average'], '10.30')
        self.assertEqual(
            response.json()['data']['substitution']['replaced_component_id'],
            str(self.exam_1.public_id),
        )

    def test_rejects_component_from_another_scheme(self) -> None:
        self.authenticate()

        response = self.client.post(
            self.endpoint,
            {
                'grades': [
                    {
                        'component_id': str(uuid4()),
                        'score': '15.00',
                    },
                ],
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('grades', response.json()['error']['errors'])
