# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('populate_db', '0009_stationduplicate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='station',
            name='id',
            field=models.BigIntegerField(serialize=False, primary_key=True, db_index=True),
        ),
    ]
