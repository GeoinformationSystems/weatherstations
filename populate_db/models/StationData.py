import datetime
from django.db import models
from django.forms.models import model_to_dict

# ==============================================================================
'''
    A StationData stores the temperature and precipitation data
    for one weather station for one year for one month.

    ----------------------------------------------------------------------------
    StationData n:1 Station
'''
# ==============================================================================

class StationData(models.Model):
    # foreign key: station
    station =       models.ForeignKey       ('Station', related_name="station")

    # main attributes
    time =          models.DateField        (default='2017-01-01')
    temperature =   models.DecimalField     (max_digits=4, decimal_places=2, null=True, blank=True)
    precipitation = models.DecimalField     (max_digits=5, decimal_places=1, null=True, blank=True)

    # additional speedup attributes (might not be useful?)
    is_complete =   models.BooleanField     (default=False)


    # ----------------------------------------------------------------------------
    def __unicode__(self):
        return str(
            self.station + '|' +
            self.datetime.year + '-' +
            self.datetime.month
        )

    # ----------------------------------------------------------------------------
    class Meta:
        app_label = 'populate_db'
        ordering =  ['station', 'time']
