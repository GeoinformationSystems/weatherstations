# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('populate_db', '0005_auto_20170217_0808'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='station',
            name='prcp_max_year',
        ),
        migrations.RemoveField(
            model_name='station',
            name='prcp_min_year',
        ),
        migrations.RemoveField(
            model_name='station',
            name='temp_max_year',
        ),
        migrations.RemoveField(
            model_name='station',
            name='temp_min_year',
        ),
        migrations.AddField(
            model_name='station',
            name='coverage_rate',
            field=models.DecimalField(default=1.0, max_digits=3, decimal_places=2),
        ),
        migrations.AddField(
            model_name='station',
            name='largest_gap',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='station',
            name='max_year',
            field=models.IntegerField(default=-9999),
        ),
        migrations.AddField(
            model_name='station',
            name='min_year',
            field=models.IntegerField(default=9999),
        ),
        migrations.AddField(
            model_name='station',
            name='missing_months',
            field=models.IntegerField(default=0),
        ),
    ]
