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
    Station 1:n StationData
'''

# ==============================================================================

class Station(models.Model):

    # main attributes
    id = models.BigIntegerField \
    (
        primary_key=True,
        db_index=True
    )

    name = models.CharField \
    (
        max_length=32
    )

    country = models.CharField \
    (
        max_length=52
    )

    lat = models.DecimalField \
    (
        max_digits=4,
        decimal_places=2
    )

    lng = models.DecimalField \
    (
        max_digits=5,
        decimal_places=2
    )

    elev = models.IntegerField \
    (
        null=True
    )

    # additional speedup attributes - might not be useful?)

    ## temporal interval in which data is available for this station
    ## -> minimum and maximum year
    min_year = models.IntegerField \
    (
        default=9999
    )

    max_year = models.IntegerField \
    (
        default=-9999
    )

    ## total number of months that miss either temperature or precipitation data
    missing_months = models.IntegerField \
    (
        default=0
    )

    ## percentage of months that are covered (i.e. not missing) = [0 .. 1]
    complete_data_rate = models.DecimalField \
    (
        default=1.0,
        max_digits=3,
        decimal_places=2
    )

    # largest number of consecutive missing months
    largest_gap = models.IntegerField \
    (
        default=0
    )

    # ----------------------------------------------------------------------------
    def __unicode__(self):
        return str(self.name)

    # ----------------------------------------------------------------------------
    class Meta:
        app_label = 'populate_db'
        ordering =  ['id']
