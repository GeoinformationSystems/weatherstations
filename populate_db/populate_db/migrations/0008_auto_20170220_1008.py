# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('populate_db', '0007_auto_20170219_1506'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='station',
            options={'ordering': ['id']},
        ),
    ]
