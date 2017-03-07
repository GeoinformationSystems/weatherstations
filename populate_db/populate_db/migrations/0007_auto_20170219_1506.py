# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('populate_db', '0006_auto_20170217_1151'),
    ]

    operations = [
        migrations.RenameField(
            model_name='station',
            old_name='coverage_rate',
            new_name='complete_data_rate',
        ),
    ]
