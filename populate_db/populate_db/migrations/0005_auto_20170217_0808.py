# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('populate_db', '0004_auto_20170215_1441'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stationdata',
            options={'ordering': ['station', 'year', 'month']},
        ),
        migrations.RemoveField(
            model_name='stationdata',
            name='time',
        ),
        migrations.AddField(
            model_name='stationdata',
            name='month',
            field=models.PositiveSmallIntegerField(default=b'1'),
        ),
        migrations.AddField(
            model_name='stationdata',
            name='year',
            field=models.PositiveSmallIntegerField(default=b'2017'),
        ),
    ]
