from urllib.parse import urlsplit

from django.db import migrations


GOOGLE_PROVIDER = 'google'
MAX_AVATAR_URL_LENGTH = 2048


def normalize_avatar_url(value) -> str:
    if not isinstance(value, str):
        return ''

    value = value.strip()

    if not value or len(value) > MAX_AVATAR_URL_LENGTH:
        return ''

    try:
        parsed_value = urlsplit(value)
    except ValueError:
        return ''

    if parsed_value.scheme != 'https' or not parsed_value.netloc:
        return ''

    return value


def populate_user_google_identity(apps, schema_editor) -> None:
    SocialAccount = apps.get_model(
        'socialaccount',
        'SocialAccount',
    )
    User = apps.get_model(
        'accounts',
        'User',
    )

    database_alias = schema_editor.connection.alias
    processed_user_ids: set[int] = set()

    social_accounts = (
        SocialAccount.objects.using(database_alias)
        .filter(provider=GOOGLE_PROVIDER)
        .order_by('pk')
        .values(
            'user_id',
            'uid',
            'extra_data',
        )
    )

    for social_account in social_accounts.iterator():
        user_id = social_account['user_id']

        if user_id in processed_user_ids:
            continue

        raw_google_subject = social_account['uid']

        if not isinstance(raw_google_subject, str):
            continue

        google_subject = raw_google_subject.strip()

        if not google_subject:
            continue

        extra_data = social_account['extra_data']

        if isinstance(extra_data, dict):
            picture = extra_data.get('picture')
        else:
            picture = None

        avatar_url = normalize_avatar_url(picture)

        user = (
            User.objects.using(database_alias)
            .filter(pk=user_id)
            .first()
        )

        if user is None:
            continue

        updates: dict[str, object] = {}

        if user.google_subject is None:
            updates['google_subject'] = google_subject
        elif user.google_subject != google_subject:
            processed_user_ids.add(user_id)
            continue

        if not user.avatar_url and avatar_url:
            updates['avatar_url'] = avatar_url

        if updates:
            (
                User.objects.using(database_alias)
                .filter(pk=user_id)
                .update(**updates)
            )

        processed_user_ids.add(user_id)


class Migration(migrations.Migration):
    dependencies = [
        (
            'accounts',
            '0010_user_avatar_url_user_google_subject',
        ),
        (
            'socialaccount',
            '0006_alter_socialaccount_extra_data',
        ),
    ]

    operations = [
        migrations.RunPython(
            populate_user_google_identity,
            migrations.RunPython.noop,
        ),
    ]