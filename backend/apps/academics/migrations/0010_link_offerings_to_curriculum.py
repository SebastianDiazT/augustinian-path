from django.db import migrations, models


def link_offerings_to_curriculum(apps, schema_editor):
    CourseOffering = apps.get_model('academics', 'CourseOffering')
    CurriculumCourse = apps.get_model('academics', 'CurriculumCourse')
    through_model = CourseOffering.curriculum_courses.through

    relations = []

    for offering in CourseOffering.objects.iterator():
        curriculum_course_ids = CurriculumCourse.objects.filter(
            course_id=offering.course_id,
        ).values_list(
            'pk',
            flat=True,
        )

        relations.extend(
            through_model(
                courseoffering_id=offering.pk,
                curriculumcourse_id=curriculum_course_id,
            )
            for curriculum_course_id in curriculum_course_ids
        )

    through_model.objects.bulk_create(
        relations,
        ignore_conflicts=True,
    )


def unlink_offerings_from_curriculum(apps, schema_editor):
    CourseOffering = apps.get_model('academics', 'CourseOffering')
    CourseOffering.curriculum_courses.through.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('academics', '0009_add_curriculum_prerequisites'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseoffering',
            name='curriculum_courses',
            field=models.ManyToManyField(
                blank=True,
                related_name='course_offerings',
                to='academics.curriculumcourse',
            ),
        ),
        migrations.RunPython(
            link_offerings_to_curriculum,
            unlink_offerings_from_curriculum,
        ),
    ]
