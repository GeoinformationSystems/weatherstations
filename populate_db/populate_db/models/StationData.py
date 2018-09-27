from django.db import models

# ==============================================================================
'''
    A StationData stores the temperature and precipitation data
    for one weather station for one year for one month.

    ----------------------------------------------------------------------------
    StationData n:1 Station
'''


# ==============================================================================

class StationData(models.Model):
    id = models.BigIntegerField(
        primary_key=True,
        db_index=True
    )

    # foreign key
    station = models.ForeignKey(
        'Station',
        related_name="station",
        db_index=True
    )

    # main attributes
    year = models.PositiveSmallIntegerField(
        default='2017'
    )

    month = models.PositiveSmallIntegerField(
        default='1'
    )

    temperature = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        default=None
    )

    precipitation = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        default=None
    )

    # additional speedup attributes (might not be useful?)
    is_complete = models.BooleanField(
        default=False
    )

    # ----------------------------------------------------------------------------
    def __unicode__(self):
        if self.month > 10:
            month_pad = ''
        else:
            month_pad = '0'
        return str(
            str(self.station) + '|' +
            str(self.year) + '-' +
            month_pad +
            str(self.month)
        )

    # ----------------------------------------------------------------------------
    class Meta:
        app_label = 'populate_db'
        ordering = ['id']
