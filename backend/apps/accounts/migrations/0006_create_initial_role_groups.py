from django.db import migrations


ROLE_NAMES = (
    'student',
    'platform_admin',
)


def create_initial_role_groups(apps, schema_editor) -> None:
    Group = apps.get_model('auth', 'Group')
    database_alias = schema_editor.connection.alias

    for role_name in ROLE_NAMES:
        Group.objects.using(database_alias).get_or_create(
            name=role_name,
        )


def delete_initial_role_groups(apps, schema_editor) -> None:
    Group = apps.get_model('auth', 'Group')
    database_alias = schema_editor.connection.alias

    Group.objects.using(database_alias).filter(
        name__in=ROLE_NAMES,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        (
            'accounts',
            '0005_enforce_user_public_id',
        ),
    ]

    operations = [
        migrations.RunPython(
            create_initial_role_groups,
            delete_initial_role_groups,
        ),
    ]