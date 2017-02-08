################################################################################
# CREATE AND POPULATE THE CLIMATE DATA BASE WITH
# STATIONS AND THEIR HISTORICAL TEMPERATURE AND PRECIPITATION DATA
################################################################################

# execute me using:
# python manage.py popdb

################################################################################
# GLOBAL CONSTANTS
################################################################################

INPUT_FILES = \
{
    'country_codes':    'data/meta/country_codes',
    'temperature' :
    {
        'stations':     'data/GHCN_monthly_v3_temperature/ghcnm.tavg.v3.3.0.20170203.qca.inv',
        'data':         'data/GHCN_monthly_v3_temperature/ghcnm.tavg.v3.3.0.20170203.qca.dat'
    },
    'precipitation' :
    {
        'stations':     'data/GHCN_monthly_v2_precipitation/v2.prcp.inv',
        'data':         'data/GHCN_monthly_v2_precipitation/v2.prcp'
    }
}

LNG_MAX = 180.0
LAT_MAX =  90.0

################################################################################
# INCLUDES
################################################################################

# general python modules
import os

# django modules
from django.core.management.base import BaseCommand, CommandError, NoArgsCommand
from django.conf import settings

# own modules
from populate_db.models import *

################################################################################
# HELPER FUNCTIONS
################################################################################

# ------------------------------------------------------------------------------
def get_file(file_id):
    return os.path.abspath(
        os.path.join(
            os.path.dirname(populate_db.__file__),
            file_id
    )
)


################################################################################
# MAIN
################################################################################

class Command(NoArgsCommand):
    help = 'populates the database with initial data'

    def handle_noargs(self, **options):
        print("HORST")

        # cleanup
        Station.objects.all().delete()
        TemperatureData.objects.all().delete()
        PrecipitationData.objects.all().delete()

        teststation = Station(
            name = "Horst",
            country = "Horstland",
            lat = 0,
            lng = 0,
            elev = 0
        )
        teststation.save()
