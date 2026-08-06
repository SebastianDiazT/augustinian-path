from decimal import Decimal

from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import (
    AcademicPeriod,
    Course,
    CourseOffering,
    CurriculumCourse,
    CurriculumPlan,
    Faculty,
    ProfessionalSchool,
)
from apps.accounts.models import User
from apps.accounts.roles import Role
from apps.syllabi.models import Syllabus


class SyllabusApiTests(APITestCase):
    admin_endpoint = '/api/v1/admin/syllabi/'
    student_endpoint = '/api/v1/syllabi/'

    def setUp(self) -> None:
        faculty = Faculty.objects.create(name='Facultad de Ingeniería')
        school = ProfessionalSchool.objects.create(
            faculty=faculty,
            name='Ingeniería de Sistemas',
        )
        plan = CurriculumPlan.objects.create(
            professional_school=school,
            code='2017',
            name='Plan 2017',
        )
        course = Course.objects.create(
            professional_school=school,
            code='1705167',
            name='Tópicos Avanzados en Bases de Datos (E)',
        )
        self.curriculum_course = CurriculumCourse.objects.create(
            curriculum_plan=plan,
            course=course,
            cycle=9,
            credits=Decimal('4.00'),
            theory_hours=Decimal('3.00'),
            practice_hours=Decimal('2.00'),
        )
        period = AcademicPeriod.objects.create(
            year=2026,
            term=AcademicPeriod.Term.FIRST,
        )
        self.offering = CourseOffering.objects.create(
            academic_period=period,
            course=course,
        )
        self.offering.curriculum_courses.add(self.curriculum_course)
        self.admin_user = User.objects.create_user(
            email='syllabus.admin@unsa.edu.pe',
            password='Prueba123!',
        )
        self.admin_user.groups.add(
            Group.objects.get(name=Role.PLATFORM_ADMIN.value),
        )
        self.student = User.objects.create_user(
            email='syllabus.student@unsa.edu.pe',
            password='Prueba123!',
        )
        self.student.groups.add(
            Group.objects.get(name=Role.STUDENT.value),
        )

    def published_payload(self) -> dict[str, object]:
        return {
            'course_offering_id': str(self.offering.public_id),
            'curriculum_course_id': str(self.curriculum_course.public_id),
            'status': Syllabus.Status.PUBLISHED,
            'duration_weeks': 2,
            'publication_date': '2026-04-06',
            'foundation': 'Procesamiento de datos vectoriales y RAG.',
            'instructors': [
                {
                    'name': 'Arroyo Paz, Antonio',
                    'academic_degree': 'Magíster',
                    'academic_department': 'Ingeniería de Sistemas',
                    'weekly_hours': '5.00',
                    'schedule': [
                        'Lun 11:30-13:10',
                        'Mié 07:00-09:40',
                    ],
                }
            ],
            'competencies': [
                {
                    'code': 'C.I.',
                    'description': 'Gestiona proyectos aplicando bases de datos.',
                }
            ],
            'thematic_content': [
                {
                    'order': 1,
                    'title': 'Primera unidad',
                    'chapters': [
                        {
                            'title': 'Bases de datos vectoriales',
                            'topics': [
                                {
                                    'number': 1,
                                    'title': 'Introducción',
                                },
                                {
                                    'number': 2,
                                    'title': 'Embeddings',
                                },
                            ],
                        }
                    ],
                }
            ],
            'teaching_methods': 'Clases magistrales y casos prácticos.',
            'teaching_media': 'Aula virtual y videoconferencias.',
            'organization_forms': 'Clases teóricas y prácticas.',
            'formative_research': 'Trabajo de investigación formativa.',
            'social_responsibility': 'Actividades de responsabilidad social.',
            'weekly_schedule': [
                {
                    'week': 1,
                    'topic': 'Introducción',
                    'instructor': 'A. Arroyo',
                    'percentage': '50.00',
                    'cumulative_percentage': '50.00',
                },
                {
                    'week': 2,
                    'topic': 'Embeddings',
                    'instructor': 'A. Arroyo',
                    'percentage': '50.00',
                    'cumulative_percentage': '100.00',
                },
            ],
            'evaluation_strategy': 'Evaluación continua y periódica.',
            'evaluation_schedule': [
                {
                    'name': 'Primera evaluación',
                    'evaluation_date': '2026-05-13',
                    'theory_weight': '20.00',
                    'continuous_weight': '30.00',
                    'total_weight': '50.00',
                },
                {
                    'name': 'Segunda evaluación',
                    'evaluation_date': '2026-06-24',
                    'theory_weight': '20.00',
                    'continuous_weight': '30.00',
                    'total_weight': '50.00',
                },
            ],
            'approval_requirements': 'Promedio final igual o mayor a 10.50.',
            'bibliography': [
                {
                    'category': 'BASIC',
                    'citation': 'N. Borwankar, Vector Databases, 2024.',
                    'url': 'https://example.com/vector-databases',
                },
                {
                    'category': 'CONSULTATION',
                    'citation': 'Sentence-BERT, EMNLP 2019.',
                    'url': 'https://example.com/sentence-bert',
                },
            ],
            'source_document_url': 'https://example.com/syllabus.pdf',
        }

    def test_admin_creates_published_structured_syllabus(self) -> None:
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            self.admin_endpoint,
            self.published_payload(),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()['data']
        self.assertEqual(data['course_code'], '1705167')
        self.assertEqual(data['academic_period_code'], '2026-A')
        self.assertEqual(data['theory_schedule_hours'], '5.00')
        self.assertEqual(len(data['weekly_schedule']), 2)

    def test_student_only_sees_published_syllabus(self) -> None:
        self.client.force_authenticate(user=self.admin_user)
        created = self.client.post(
            self.admin_endpoint,
            self.published_payload(),
            format='json',
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.client.force_authenticate(user=self.student)

        response = self.client.get(self.student_endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['data']['syllabi']), 1)

    def test_rejects_published_syllabus_with_incomplete_weeks(self) -> None:
        payload = self.published_payload()
        payload['weekly_schedule'] = payload['weekly_schedule'][:1]
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            self.admin_endpoint,
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('weekly_schedule', response.json()['error']['errors'])
