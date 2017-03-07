# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('populate_db', '0002_auto_20170215_1027'),
    ]

    operations = [
        migrations.CreateModel(
            name='StationData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateField(default=b'2017-01-01')),
                ('temperature', models.DecimalField(null=True, max_digits=4, decimal_places=2, blank=True)),
                ('precipitation', models.DecimalField(null=True, max_digits=5, decimal_places=1, blank=True)),
                ('is_complete', models.BooleanField(default=False)),
                ('station', models.ForeignKey(related_name='station', to='populate_db.Station')),
            ],
            options={
                'ordering': ['station', 'time'],
            },
        ),
        migrations.RemoveField(
            model_name='precipitationdata',
            name='station',
        ),
        migrations.RemoveField(
            model_name='temperaturedata',
            name='station',
        ),
        migrations.DeleteModel(
            name='PrecipitationData',
        ),
        migrations.DeleteModel(
            name='TemperatureData',
        ),
    ]
