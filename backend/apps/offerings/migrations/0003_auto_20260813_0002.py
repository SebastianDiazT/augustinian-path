from datetime import time

from django.db import migrations


def create_time_blocks(apps, schema_editor):
    TimeBlock = apps.get_model('offerings', 'TimeBlock')

    blocks = [
        (1, time(7, 0), time(7, 50)),
        (2, time(7, 50), time(8, 40)),
        (3, time(8, 50), time(9, 40)),
        (4, time(9, 40), time(10, 30)),
        (5, time(10, 40), time(11, 30)),
        (6, time(11, 30), time(12, 20)),
        (7, time(12, 20), time(13, 10)),
        (8, time(13, 10), time(14, 0)),
        (9, time(14, 0), time(14, 50)),
        (10, time(14, 50), time(15, 40)),
        (11, time(15, 50), time(16, 40)),
        (12, time(16, 40), time(17, 30)),
        (13, time(17, 40), time(18, 30)),
        (14, time(18, 30), time(19, 20)),
    ]

    for order, start, end in blocks:
        TimeBlock.all_objects.get_or_create(
            order=order,
            defaults={
                'start_time': start,
                'end_time': end,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('offerings', '0002_alter_offering_options_alter_section_options'),
    ]

    operations = [
        migrations.RunPython(create_time_blocks),
    ]
