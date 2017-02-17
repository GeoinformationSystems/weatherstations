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
        primary_key=True
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
    temp_min_year = models.IntegerField \
    (
        null=True
    )
    temp_max_year = models.IntegerField \
    (
        null=True
    )
    prcp_min_year = models.IntegerField \
    (
        null=True
    )
    prcp_max_year = models.IntegerField \
    (
        null=True
    )


    # ----------------------------------------------------------------------------
    def __unicode__(self):
        return str(self.name)

    # ----------------------------------------------------------------------------
    class Meta:
        app_label = 'populate_db'
