# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('populate_db', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='precipitationdata',
            options={'ordering': ['station', 'year']},
        ),
        migrations.AlterModelOptions(
            name='temperaturedata',
            options={'ordering': ['station', 'year']},
        ),
    ]
