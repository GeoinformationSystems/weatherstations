################################################################################
# CREATE STATISTICS ABOUT THE QUALITY OF THE DATA IN THE CLIMATE DATABASE
################################################################################

# execute me using:
# python manage.py statistics


################################################################################
# INCLUDES
################################################################################

# general python modules

# django modules
from django.core.management.base import BaseCommand
from django.db.models import *

# own modules
from populate_db.models import *
from input_data import *
################################################################################
# GLOBAL CONSTANTS
################################################################################

# number of characters for maxmimum length of ... for the statistics
JUST_WIDTH = {
    'description': 40,  # maximum length of describing text
    'number': 10,  # maximum length of number
    'rate': 8,  # maximum length of rate [%]
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
            str("RATE").rjust(JUST_WIDTH['rate'])
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
    if total_number is not None:
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

        # promising stations with decent coverage
        promising_stations = Station.objects \
            .filter(complete_data_rate__gte=MIN_COVERAGE) \
            .filter(largest_gap__lte=MAX_GAPS)
        print_stat(
            "promising stations with decent coverage",
            promising_stations.count(),
            num_stations
        )

        # ======================================================================
        # TEMPERATURE AND PRECIPITATION DATA
        # ======================================================================

        print_header("CLIMATE DATA")

        promising_station_data = StationData.objects.filter(station=promising_stations)

        # reference values
        num_records = promising_station_data.count()

        # number of stations
        print_stat(
            "total station data records",
            num_records,
            num_records
        )

        # earliest (min) and latest (max) year of record
        min_year = promising_station_data.aggregate(Min('year'))['year__min']
        max_year = promising_station_data.aggregate(Max('year'))['year__max']

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

        # count gaps (number of consecutive months with missing data)
        gaps = {
            'tmp': [0] * (MAX_GAP + 1),  # MAGIC! initialize list with n 0-elements
            'prc': [0] * (MAX_GAP + 1)  # MAGIC! initialize list with n 0-elements
        }

        # for each Station
        # for station in Station.objects.filter(name='Tillabery'):
        for station in promising_stations:

            # get all monthly data for this station
            data_records = promising_station_data.filter(station=station)

            # compile consective list of monthly data values
            data_list = {
                'tmp': [],
                'prc': []
            }

            for data_record in data_records:
                tmp = data_record.temperature
                prc = data_record.precipitation
                if tmp is not None:
                    tmp = float(tmp)
                if prc is not None:
                    prc = float(prc)
                data_list['tmp'].append(tmp)
                data_list['prc'].append(prc)

            # for both temperature and precipitation identify gaps
            for data_key, data_values in data_list.iteritems():

                # identify gaps
                in_gap = False
                gap_size = 0

                # for each data point
                for data_value in data_values:

                    # determine if it is a gap
                    is_gap = data_value is None

                    # 4 cases:
                    # 1) currently in a gap
                    if in_gap:
                        # 1.1) gap continues -> increment!
                        if is_gap:
                            gap_size += 1
                        # 1.2) gap ended -> finalize!
                        # -> gap size n has one more occurence
                        else:
                            gaps[data_key][gap_size] += 1
                            gap_size = 0
                            in_gap = False

                    # 2) currently not in a gap
                    else:
                        # 2.1) gap found -> start new gap
                        if is_gap:
                            gap_size = 1
                            in_gap = True
                        # 2.2) no gap found -> continue!
                        else:
                            pass

                # border case: if gap reached all the way to the end, finalize again
                if in_gap:
                    gaps[data_key][gap_size] += 1
                    gap_size = 0
                    in_gap = False

        # print gaps
        for gap_key, gap_value in gaps.iteritems():

            print_header("GAPS IN " + gap_key)

            num_gaps = sum(gap_value)

            print_stat(
                "total number of gaps",
                num_gaps,
                num_gaps
            )

            for gap_size, gaps_of_size in enumerate(gap_value):
                if gaps_of_size > 0:
                    print_stat(
                        "  gap size " + str(gap_size),
                        gaps_of_size,
                        num_gaps
                    )
