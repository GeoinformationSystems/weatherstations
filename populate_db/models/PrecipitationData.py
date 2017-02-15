from django.db import models
from django.forms.models import model_to_dict

# ==============================================================================
'''
    PrecipitationData represents a dataset entry for the total precipitation
    in a month for one station for one full year (12 months).
    The precipitation is given in millimeters with 1 decimal place.

    ----------------------------------------------------------------------------
    PrecipitationData n:1 Station
'''
# ==============================================================================

class PrecipitationData(models.Model):

    # foreign key: station
    station =       models.ForeignKey       ('Station', related_name="station_precipitation")

    # main attributes
    year =          models.IntegerField     (default=0)
    m01 =           models.DecimalField     (max_digits=5, decimal_places=1, null=True, blank=True)
    m02 =           models.DecimalField     (max_digits=5, decimal_places=1, null=True, blank=True)
    m03 =           models.DecimalField     (max_digits=5, decimal_places=1, null=True, blank=True)
    m04 =           models.DecimalField     (max_digits=5, decimal_places=1, null=True, blank=True)
    m05 =           models.DecimalField     (max_digits=5, decimal_places=1, null=True, blank=True)
    m06 =           models.DecimalField     (max_digits=5, decimal_places=1, null=True, blank=True)
    m07 =           models.DecimalField     (max_digits=5, decimal_places=1, null=True, blank=True)
    m08 =           models.DecimalField     (max_digits=5, decimal_places=1, null=True, blank=True)
    m09 =           models.DecimalField     (max_digits=5, decimal_places=1, null=True, blank=True)
    m10 =           models.DecimalField     (max_digits=5, decimal_places=1, null=True, blank=True)
    m11 =           models.DecimalField     (max_digits=5, decimal_places=1, null=True, blank=True)
    m12 =           models.DecimalField     (max_digits=5, decimal_places=1, null=True, blank=True)

    # ----------------------------------------------------------------------------
    def __unicode__(self):
        return str(self.year)

    # ----------------------------------------------------------------------------
    class Meta:
        app_label = 'populate_db'
        ordering =  ['station', 'year']
