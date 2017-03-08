# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('populate_db', '0008_auto_20170220_1008'),
    ]

    operations = [
        migrations.CreateModel(
            name='StationDuplicate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('duplicate_station', models.BigIntegerField(default=0, db_index=True)),
                ('master_station', models.ForeignKey(related_name='master_station', to='populate_db.Station')),
            ],
        ),
    ]
