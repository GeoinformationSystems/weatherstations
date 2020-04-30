from django.db import models

# ==============================================================================
'''
    A StationDuplicate represents a connection between two weather stations
    that are considered "equal", i.e:
    - Only the last three digits of the id are different
    - The same is very close
    - They are not more than 2 km away from each other
    -> it is probably an updated station

    This Table is only for import purposes
    ----------------------------------------------------------------------------
    Station 1:n StationData
'''


# ==============================================================================

class StationDuplicate(models.Model):
    # main attributes
    duplicate_station = models.BigIntegerField(
        default=0,
        db_index=True
    )

    master_station = models.ForeignKey(
        'Station',
        related_name='master_station',
        on_delete=models.CASCADE,
        db_index=True
    )

    # ----------------------------------------------------------------------------
    def __unicode__(self):
        return str(self.master_station.name)

    # ----------------------------------------------------------------------------
    class Meta:
        app_label = 'populate_db'
