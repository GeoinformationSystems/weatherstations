from django.db import models

# Create your models here.

from django.db import models
from django.forms.models import model_to_dict

# ==============================================================================
'''
    A Station represents a weather station as a geographic object. It has a
    name, a geographic location (lat, lng and alt) and is located in a country.
    Additionally it provides information to speed up the data query process:
      time span in which temperature data is available (min and max year)
      time span in which precipitation data is available (min and max year)

    ----------------------------------------------------------------------------
    Station 1:n TemperatureData
    Station 1:n PrecipitationData
'''

class Station(models.Model):

    # main attributes
    name =          models.CharField    (max_length=32)
    country =       models.CharField    (max_length=52)
    lat =           models.DecimalField (max_digits=5, decimal_places=2)
    lng =           models.DecimalField (max_digits=4, decimal_places=2)
    elev =          models.IntegerField (null=True)

    # additional speedup attributes (might not be useful?)
    temp_min_year = models.IntegerField (null=True)
    temp_max_year = models.IntegerField (null=True)
    prcp_min_year = models.IntegerField (null=True)
    prcp_max_year = models.IntegerField (null=True)


# ==============================================================================
'''
    TemperatureData represents a dataset entry for the average temperature
    in a month for one station for one full year (12 months).
    The temperature is given in degree Celsius with 2 decimal places.

    ----------------------------------------------------------------------------
    TemperatureData n:1 Station
'''

class TemperatureData(models.Model):

    # foreign key: station
    station =       models.ForeignKey       ('Station', related_name="station_temperature")

    # main attributes
    year =          models.IntegerField     (default=0)
    m01 =           models.DecimalField     (max_digits=4, decimal_places=2, null=True)
    m02 =           models.DecimalField     (max_digits=4, decimal_places=2, null=True)
    m03 =           models.DecimalField     (max_digits=4, decimal_places=2, null=True)
    m04 =           models.DecimalField     (max_digits=4, decimal_places=2, null=True)
    m05 =           models.DecimalField     (max_digits=4, decimal_places=2, null=True)
    m06 =           models.DecimalField     (max_digits=4, decimal_places=2, null=True)
    m07 =           models.DecimalField     (max_digits=4, decimal_places=2, null=True)
    m08 =           models.DecimalField     (max_digits=4, decimal_places=2, null=True)
    m09 =           models.DecimalField     (max_digits=4, decimal_places=2, null=True)
    m10 =           models.DecimalField     (max_digits=4, decimal_places=2, null=True)
    m11 =           models.DecimalField     (max_digits=4, decimal_places=2, null=True)
    m12 =           models.DecimalField     (max_digits=4, decimal_places=2, null=True)


# ==============================================================================
'''
    PrecipitationData represents a dataset entry for the total precipitation
    in a month for one station for one full year (12 months).
    The precipitation is given in millimeters with 1 decimal place.

    ----------------------------------------------------------------------------
    PrecipitationData n:1 Station
'''

class PrecipitationData(models.Model):

    # foreign key: station
    station =       models.ForeignKey       ('Station', related_name="station_precipitation")

    # main attributes
    year =          models.IntegerField     (default=0)
    m01 =           models.DecimalField     (max_digits=5, decimal_places=1, null=True)
    m02 =           models.DecimalField     (max_digits=5, decimal_places=2, null=True)
    m03 =           models.DecimalField     (max_digits=5, decimal_places=2, null=True)
    m04 =           models.DecimalField     (max_digits=5, decimal_places=2, null=True)
    m05 =           models.DecimalField     (max_digits=5, decimal_places=2, null=True)
    m06 =           models.DecimalField     (max_digits=5, decimal_places=2, null=True)
    m07 =           models.DecimalField     (max_digits=5, decimal_places=2, null=True)
    m08 =           models.DecimalField     (max_digits=5, decimal_places=2, null=True)
    m09 =           models.DecimalField     (max_digits=5, decimal_places=2, null=True)
    m10 =           models.DecimalField     (max_digits=5, decimal_places=2, null=True)
    m11 =           models.DecimalField     (max_digits=5, decimal_places=2, null=True)
    m12 =           models.DecimalField     (max_digits=5, decimal_places=2, null=True)
