# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-07-25 09:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('populate_db', '0011_auto_20180723_0855'),
    ]

    operations = [
        migrations.AddField(
            model_name='station',
            name='station_id',
            field=models.BigIntegerField(null=True),
        ),
    ]
