# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PrecipitationData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(default=0)),
                ('m01', models.DecimalField(null=True, max_digits=5, decimal_places=1)),
                ('m02', models.DecimalField(null=True, max_digits=5, decimal_places=2)),
                ('m03', models.DecimalField(null=True, max_digits=5, decimal_places=2)),
                ('m04', models.DecimalField(null=True, max_digits=5, decimal_places=2)),
                ('m05', models.DecimalField(null=True, max_digits=5, decimal_places=2)),
                ('m06', models.DecimalField(null=True, max_digits=5, decimal_places=2)),
                ('m07', models.DecimalField(null=True, max_digits=5, decimal_places=2)),
                ('m08', models.DecimalField(null=True, max_digits=5, decimal_places=2)),
                ('m09', models.DecimalField(null=True, max_digits=5, decimal_places=2)),
                ('m10', models.DecimalField(null=True, max_digits=5, decimal_places=2)),
                ('m11', models.DecimalField(null=True, max_digits=5, decimal_places=2)),
                ('m12', models.DecimalField(null=True, max_digits=5, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('country', models.CharField(max_length=52)),
                ('lat', models.DecimalField(max_digits=5, decimal_places=2)),
                ('lng', models.DecimalField(max_digits=4, decimal_places=2)),
                ('elev', models.IntegerField(null=True)),
                ('temp_min_year', models.IntegerField(null=True)),
                ('temp_max_year', models.IntegerField(null=True)),
                ('prcp_min_year', models.IntegerField(null=True)),
                ('prcp_max_year', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TemperatureData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(default=0)),
                ('m01', models.DecimalField(null=True, max_digits=4, decimal_places=2)),
                ('m02', models.DecimalField(null=True, max_digits=4, decimal_places=2)),
                ('m03', models.DecimalField(null=True, max_digits=4, decimal_places=2)),
                ('m04', models.DecimalField(null=True, max_digits=4, decimal_places=2)),
                ('m05', models.DecimalField(null=True, max_digits=4, decimal_places=2)),
                ('m06', models.DecimalField(null=True, max_digits=4, decimal_places=2)),
                ('m07', models.DecimalField(null=True, max_digits=4, decimal_places=2)),
                ('m08', models.DecimalField(null=True, max_digits=4, decimal_places=2)),
                ('m09', models.DecimalField(null=True, max_digits=4, decimal_places=2)),
                ('m10', models.DecimalField(null=True, max_digits=4, decimal_places=2)),
                ('m11', models.DecimalField(null=True, max_digits=4, decimal_places=2)),
                ('m12', models.DecimalField(null=True, max_digits=4, decimal_places=2)),
                ('station', models.ForeignKey(related_name='station_temperature', to='populate_db.Station')),
            ],
        ),
        migrations.AddField(
            model_name='precipitationdata',
            name='station',
            field=models.ForeignKey(related_name='station_precipitation', to='populate_db.Station'),
        ),
    ]
