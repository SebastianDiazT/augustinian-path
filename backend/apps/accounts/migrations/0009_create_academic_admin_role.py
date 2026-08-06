from django.db import migrations

ACADEMIC_ADMIN_ROLE = 'academic_admin'


def create_academic_admin_role(
    apps,
    schema_editor,
) -> None:
    Group = apps.get_model(
        'auth',
        'Group',
    )
    database_alias = schema_editor.connection.alias

    Group.objects.using(database_alias).get_or_create(
        name=ACADEMIC_ADMIN_ROLE,
    )


def remove_academic_admin_role(
    apps,
    schema_editor,
) -> None:
    Group = apps.get_model(
        'auth',
        'Group',
    )
    database_alias = schema_editor.connection.alias

    Group.objects.using(database_alias).filter(
        name=ACADEMIC_ADMIN_ROLE,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        (
            'accounts',
            '0008_academicadminassignment',
        ),
    ]

    operations = [
        migrations.RunPython(
            create_academic_admin_role,
            remove_academic_admin_role,
        ),
    ]
