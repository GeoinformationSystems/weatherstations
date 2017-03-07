# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('populate_db', '0003_auto_20170215_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stationdata',
            name='precipitation',
            field=models.DecimalField(default=None, null=True, max_digits=5, decimal_places=1, blank=True),
        ),
        migrations.AlterField(
            model_name='stationdata',
            name='temperature',
            field=models.DecimalField(default=None, null=True, max_digits=4, decimal_places=2, blank=True),
        ),
    ]
