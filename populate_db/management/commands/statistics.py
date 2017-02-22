################################################################################
# CREATE STATISTICS ABOUT THE QUALITY OF THE DATA IN THE CLIMATE DATABASE
################################################################################

# execute me using:
# python manage.py statistics


################################################################################
# INCLUDES
################################################################################

# general python modules
import os
from decimal import *

# django modules
from django.core.management.base import BaseCommand, CommandError, NoArgsCommand
from django.conf import settings
from django.db import models, transaction
from django.db.models import *

# own modules
from populate_db.models import *
from populate_db.management.commands.input_data import *
from populate_db.management.commands.helpers import *


################################################################################
# GLOBAL CONSTANTS
################################################################################

# number of characters for maxmimum length of ... for the statistics
JUST_WIDTH = \
{
    'description':  40,     # maximum length of describing text
    'number':       10,     # maximum length of number
    'rate':         8,      # maximum length of rate [%]
}


################################################################################
# LOCAL HELPERS
################################################################################

# ------------------------------------------------------------------------------
def print_header(title):
    print ""
    print ""
    print title
    print "=" * len(title)
    print ""
    print(
        str("METRIC").ljust(JUST_WIDTH['description']) +
        "|" +
        str("TOTAL NUM").rjust(JUST_WIDTH['number']) +
        "|" +
        str("RATE").rjust(JUST_WIDTH['rate'] )
    )
    print_line()


# ------------------------------------------------------------------------------
def print_line():
    total_num_chars = 0
    for width in JUST_WIDTH:
        total_num_chars += JUST_WIDTH[width]
    print("-" * (total_num_chars + 2))


# ------------------------------------------------------------------------------
def print_stat(text, number, total_number):
    if not total_number is None:
        rate = str('%.1f' % (100 * float(number) / float(total_number))) + " %"
    else:
        rate = ''
    print(
        str(text).ljust(JUST_WIDTH['description']) +
        "|" +
        str(int(number)).rjust(JUST_WIDTH['number']) +
        "|" +
        str(rate).rjust(JUST_WIDTH['rate'])
    )


################################################################################
# MAIN
################################################################################

class Command(BaseCommand):
    help = 'Creates statistics about the quality of the data in the database.'

    def handle(self, *args, **options):


        # ======================================================================
        # WEATHER STATIONS
        # ======================================================================

        print_header("WEATHER STATIONS")

        # reference value
        num_stations = Station.objects.count()

        # number of stations
        print_stat(
            "total stations",
            num_stations,
            num_stations
        )

        # stations with a complete name
        without_name = Station.objects.filter(name='').count()
        print_stat(
            "stations with a complete name",
            num_stations - without_name,
            num_stations
        )

        # stations with a complete country name
        without_country = Station.objects.filter(country='').count()
        print_stat(
            "stations with a complete country name",
            num_stations - without_country,
            num_stations
        )

        # stations in correct lat/lng bound
        in_bounds = Station.objects \
            .filter(lat__gte = -MAX_LAT) \
            .filter(lat__lte =  MAX_LAT) \
            .filter(lng__gte = -MAX_LNG) \
            .filter(lng__lte =  MAX_LNG) \
            .count()

        print_stat(
            "stations in correct lat/lng bounds",
            in_bounds,
            num_stations
        )


        # ======================================================================
        # TEMPERATURE AND PRECIPITATION DATA
        # ======================================================================

        print_header("WEATHER DATA")

        # reference values
        num_records = StationData.objects.count()

        # number of stations
        print_stat(
            "total station data records",
            num_records,
            num_records
        )

        # earliest (min) and latest (max) year of record
        min_year = StationData.objects.all().aggregate(Min('year'))['year__min']
        max_year = StationData.objects.all().aggregate(Max('year'))['year__max']

        print_stat(
            "minimum year",
            min_year,
            None
        )
        print_stat(
            "maximum year",
            max_year,
            None
        )

        # coverage of months in year
        print_line()
        print_stat(
            "total number of monthly data records",
            num_months,
            num_months
        )

        empty_records = 0
        for month in MONTHS:
            kwargs = {'{0}'.format(month[0]): None}
            empty_months = dataset[1].objects.filter(**kwargs).count()
            print_stat(
                "  complete data for " + month[1],
                num_records - empty_months,
                num_records
            )
            empty_records += empty_months

        print_stat(
            "complete monthly data records",
            num_months - empty_records,
            num_months
        )

        # count gaps (number of consecutive months with missing data)
        gaps = [0]*(MAX_GAP+1) # MAGIC! initialize list with n 0-elements

        # for each Station
        # for station in Station.objects.filter(name='Tillabery'):
        for station in Station.objects.all():

            # get all monthly data for this station
            data_records = dataset[1].objects.filter(station=station)

            # compile consective list of monthly data values
            data_list = []
            for data_record in data_records:
                for month in MONTHS:
                    dec = getattr(data_record,month[0])
                    if not dec is None:
                        dec = float(dec)
                    data_list.append(dec)

            # strip list left and right
            #  -> not necessary, because the visualization also has to
            # deal with missing data in the beginning / end of a year

            # identify gaps
            in_gap = False
            gap = 0
            for value in data_list:

                # 4 cases:
                # 1) currently in a gap
                if in_gap:
                    # 1.1) gap continues -> increment!
                    if value is None:
                        gap += 1
                    # 1.2) gap ended -> finalize!
                    # -> gap size n has one more occurence
                    else:
                        gaps[gap] += 1
                        gap = 0
                        in_gap = False
                # 2) currently not in a gap
                else:
                    # 2.1) gap found -> start new gap
                    if value is None:
                        gap = 1
                        in_gap = True
                    # 2.2) no gap found -> conitinue!
                    else:
                        pass

            # border case: if gap reached all the way to the end, finalize again
            if in_gap:
                gaps[gap] += 1
                gap = 0
                in_gap = False

        # print gaps
        num_gaps = sum(gaps)

        print_line()
        print_stat(
            "total number of gaps",
            num_gaps,
            num_gaps
        )

        for gap_size, gaps_of_size in enumerate(gaps):
            if gaps_of_size > 0:
                print_stat(
                    "  number of gaps with size " + str(gap_size),
                    gaps_of_size,
                    num_gaps
                )
