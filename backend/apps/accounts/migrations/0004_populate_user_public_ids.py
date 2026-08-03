from uuid import uuid4

from django.db import migrations


def populate_user_public_ids(apps, schema_editor) -> None:
    User = apps.get_model('accounts', 'User')
    database_alias = schema_editor.connection.alias

    users = User.objects.using(database_alias).filter(
        public_id__isnull=True,
    )

    for user in users.iterator():
        user.public_id = uuid4()
        user.save(
            using=database_alias,
            update_fields=['public_id'],
        )


def clear_user_public_ids(apps, schema_editor) -> None:
    User = apps.get_model('accounts', 'User')
    database_alias = schema_editor.connection.alias

    User.objects.using(database_alias).update(public_id=None)


class Migration(migrations.Migration):
    dependencies = [
        (
            'accounts',
            '0003_add_nullable_user_public_id',
        ),
    ]

    operations = [
        migrations.RunPython(
            populate_user_public_ids,
            clear_user_public_ids,
        ),
    ]