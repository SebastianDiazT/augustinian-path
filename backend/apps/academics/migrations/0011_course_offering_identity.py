from django.db import migrations, models
from django.db.models import Count


def merge_group_offerings(apps, schema_editor):
    CourseOffering = apps.get_model('academics', 'CourseOffering')
    duplicate_identities = (
        CourseOffering.objects.values(
            'academic_period_id',
            'course_id',
        )
        .annotate(total=Count('id'))
        .filter(total__gt=1)
    )

    for identity in duplicate_identities.iterator():
        offerings = list(
            CourseOffering.objects.filter(
                academic_period_id=identity['academic_period_id'],
                course_id=identity['course_id'],
            ).order_by('pk')
        )
        canonical = offerings[0]

        if not canonical.is_active and any(
            offering.is_active for offering in offerings[1:]
        ):
            canonical.is_active = True
            canonical.save(
                update_fields=['is_active'],
            )

        CourseOffering.objects.filter(
            pk__in=[offering.pk for offering in offerings[1:]],
        ).delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('academics', '0010_link_offerings_to_curriculum'),
    ]

    operations = [
        migrations.RunPython(
            merge_group_offerings,
            migrations.RunPython.noop,
        ),
        migrations.RemoveConstraint(
            model_name='courseoffering',
            name='unique_course_group_per_period_ci',
        ),
        migrations.RemoveConstraint(
            model_name='courseoffering',
            name='course_offering_group_code_not_empty',
        ),
        migrations.RemoveField(
            model_name='courseoffering',
            name='group_code',
        ),
        migrations.AlterModelOptions(
            name='courseoffering',
            options={
                'ordering': [
                    '-academic_period__year',
                    'academic_period__term',
                    'course__code',
                ],
                'verbose_name': 'oferta de asignatura',
                'verbose_name_plural': 'ofertas de asignaturas',
            },
        ),
        migrations.AddConstraint(
            model_name='courseoffering',
            constraint=models.UniqueConstraint(
                fields=(
                    'academic_period',
                    'course',
                ),
                name='unique_course_per_academic_period',
            ),
        ),
    ]
