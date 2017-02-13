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
    'country_codes':
    {
        'path':       'data/meta/country_codes',
        'characters':
        {
            'code':     [0,  2],
            'country':  [4, 60],
            'END':      60
        }
    }
    'temperature' :
    {
        'stations':
        {
            'path': 'data/GHCN_monthly_v3_temperature/ghcnm.tavg.v3.3.0.20170203.qca.inv',
            'characters':
            {
                'station_id':   [0,  10],
                'lat':          [12, 19],
                'lng':          [21, 29],
                'elv':          [31, 37],
                'name':         [38, 68],
                'country':      [58, 68],   # N.B. is inside name !!!
                'END':          107,
            }

        }
        'data':
         {
            'path': 'data/GHCN_monthly_v3_temperature/ghcnm.tavg.v3.3.0.20170203.qca.dat'
            'characters':
            {
                'station_id':   [0,  10],
                'year':         [11, 14],
                'value':        [15, 18],   # should always be 'TAVG'
                'm01':          [19, 23],
                'm02':          [27, 31],
                'm03':          [35, 39],
                'm04':          [43, 47],
                'm05':          [51, 55],
                'm06':          [59, 63],
                'm07':          [67, 71],
                'm08':          [75, 79],
                'm09':          [83, 87],
                'm10':          [91, 95],
                'm11':          [99, 103],
                'm12':          [107, 111],
            }
         }
    },
    'precipitation' :
    {
        'stations':
        {
            'path': 'data/GHCN_monthly_v2_precipitation/v2.prcp.inv',
            'characters':
            {
                'station_id':   [0,  10],
                'lat':          [44, 48],
                'lng':          [50, 57],
                'elv':          [58, 61],
                'name':         [12, 42],
                'country':      [32, 42],   # N.B. is inside name !!!
                'END':          107,
            }
        }
        'data':
        {
            'path': 'data/GHCN_monthly_v2_precipitation/v2.prcp',
            'characters':
            {
                'station_id':       [0,  10],
                'year':             [12, 15],
                'has_duplicates':   [11, 11],
                'm01':              [16, 20],
                'm02':              [21, 25],
                'm03':              [26, 30],
                'm04':              [31, 35],
                'm05':              [36, 40],
                'm06':              [41, 45],
                'm07':              [46, 50],
                'm08':              [51, 55],
                'm09':              [56, 60],
                'm10':              [61, 65],
                'm11':              [66, 70],
                'm12':              [71, 75],
            }
        }
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

        # preparation: read the country codes
        country_codes_file = open(get_file(INPUT_FILES.country_codes.path))
        print(country_codes_file)

        # TEMPERATURE


        # PRECIPITATION


        # example code: how to populate the database
        # teststation = Station(
        #     name = "Horst",
        #     country = "Horstland",
        #     lat = 0,
        #     lng = 0,
        #     elev = 0
        # )
        # teststation.save()
