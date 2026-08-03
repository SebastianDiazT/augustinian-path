from django.db import migrations


STUDENT_ROLE = 'student'
GOOGLE_PROVIDER = 'google'


def assign_student_role(apps, schema_editor) -> None:
    Group = apps.get_model('auth', 'Group')
    SocialAccount = apps.get_model(
        'socialaccount',
        'SocialAccount',
    )
    User = apps.get_model('accounts', 'User')

    database_alias = schema_editor.connection.alias

    student_group = Group.objects.using(database_alias).get(
        name=STUDENT_ROLE,
    )

    user_ids = list(
        SocialAccount.objects.using(database_alias)
        .filter(provider=GOOGLE_PROVIDER)
        .values_list('user_id', flat=True)
    )

    through_model = User.groups.through

    memberships = [
        through_model(
            user_id=user_id,
            group_id=student_group.id,
        )
        for user_id in user_ids
    ]

    through_model.objects.using(database_alias).bulk_create(
        memberships,
        ignore_conflicts=True,
    )


def remove_student_role(apps, schema_editor) -> None:
    Group = apps.get_model('auth', 'Group')
    SocialAccount = apps.get_model(
        'socialaccount',
        'SocialAccount',
    )
    User = apps.get_model('accounts', 'User')

    database_alias = schema_editor.connection.alias

    student_group = Group.objects.using(database_alias).get(
        name=STUDENT_ROLE,
    )

    user_ids = list(
        SocialAccount.objects.using(database_alias)
        .filter(provider=GOOGLE_PROVIDER)
        .values_list('user_id', flat=True)
    )

    User.groups.through.objects.using(database_alias).filter(
        user_id__in=user_ids,
        group_id=student_group.id,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        (
            'accounts',
            '0006_create_initial_role_groups',
        ),
        (
            'socialaccount',
            '0006_alter_socialaccount_extra_data',
        ),
    ]

    operations = [
        migrations.RunPython(
            assign_student_role,
            remove_student_role,
        ),
    ]