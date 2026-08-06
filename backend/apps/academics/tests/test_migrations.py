from decimal import Decimal

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class CourseOfferingIdentityMigrationTests(TransactionTestCase):
    migrate_from = [
        ('academics', '0009_add_curriculum_prerequisites'),
    ]
    migrate_to = [
        ('academics', '0011_course_offering_identity'),
    ]

    def test_links_curriculum_and_merges_previous_groups(self) -> None:
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        old_apps = executor.loader.project_state(self.migrate_from).apps

        Faculty = old_apps.get_model('academics', 'Faculty')
        ProfessionalSchool = old_apps.get_model(
            'academics',
            'ProfessionalSchool',
        )
        CurriculumPlan = old_apps.get_model('academics', 'CurriculumPlan')
        Course = old_apps.get_model('academics', 'Course')
        CurriculumCourse = old_apps.get_model('academics', 'CurriculumCourse')
        AcademicPeriod = old_apps.get_model('academics', 'AcademicPeriod')
        CourseOffering = old_apps.get_model('academics', 'CourseOffering')

        faculty = Faculty.objects.create(
            name='Facultad de Ingeniería',
        )
        school = ProfessionalSchool.objects.create(
            faculty=faculty,
            name='Ingeniería de Sistemas',
        )
        plan = CurriculumPlan.objects.create(
            professional_school=school,
            code='2017',
            name='Plan de Estudios 2017',
        )
        course = Course.objects.create(
            professional_school=school,
            code='1701106',
            name='Fundamentos de la Programación 1',
        )
        curriculum_course = CurriculumCourse.objects.create(
            curriculum_plan=plan,
            course=course,
            cycle=1,
            credits=Decimal('5.00'),
        )
        period = AcademicPeriod.objects.create(
            year=2026,
            term='A',
        )
        canonical = CourseOffering.objects.create(
            academic_period=period,
            course=course,
            group_code='A',
            is_active=False,
        )
        CourseOffering.objects.create(
            academic_period=period,
            course=course,
            group_code='B',
            is_active=True,
        )

        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_to)
        new_apps = executor.loader.project_state(self.migrate_to).apps
        MigratedOffering = new_apps.get_model('academics', 'CourseOffering')

        offerings = list(MigratedOffering.objects.all())

        self.assertEqual(len(offerings), 1)
        self.assertEqual(offerings[0].pk, canonical.pk)
        self.assertTrue(offerings[0].is_active)
        self.assertEqual(
            list(
                offerings[0].curriculum_courses.values_list(
                    'pk',
                    flat=True,
                )
            ),
            [curriculum_course.pk],
        )
