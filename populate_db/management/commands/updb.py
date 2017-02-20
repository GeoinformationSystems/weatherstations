################################################################################
# UPDATE THE CLIMATE DATABASE (STATIONS) WITH STATISTICALLY RELEVANT DATA
################################################################################

# execute me using:
# python manage.py updb


################################################################################
# GLOBAL CONSTANTS
################################################################################

# check only limited set of data
TEST_RUN = True

# size of consecutive database queries that are executed at once
# optimal: [1000 .. 5000]
BULK_SIZE = 50

# number of months in a year
NUM_MONTHS = 12
MONTHS = \
[
    ['m01', 'Jan'], ['m02', 'Feb'], ['m03', 'Mar'],
    ['m04', 'Apr'], ['m05', 'May'], ['m06', 'Jun'],
    ['m07', 'Jul'], ['m08', 'Aug'], ['m09', 'Sep'],
    ['m10', 'Oct'], ['m11', 'Nov'], ['m12', 'Dec']
]


# max. possible number of gaps (consecutive months with missing data) to count
MAX_GAP = 10000


################################################################################
# INCLUDES
################################################################################

# general python modules
import os
import time

# django modules
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import models, transaction
from django.db.models import *

# own modules
from populate_db.models import *
from populate_db.management.commands.input_data import *
from populate_db.management.commands.helpers import *


################################################################################
# MAIN
################################################################################

class Command(BaseCommand):
    help = "Updates the Stations in the climate database with statistically \
            relevant data: \
            - min_year and max_year: first and last year of weather data \
            - missing_months: total number of months that miss either T or P \
            - complete_data_rate: percentage of months that are covered \
            - largest_gap: largest number of consecutive missing months"


    # ==========================================================================
    # MAIN
    # ==========================================================================

    def handle(self, *args, **options):

        # speedup: manual database commits in bulks
        transaction.set_autocommit(False)

        # preparation for time management
        station_ctr =       0
        start_time =        time.time()
        intermediate_time = start_time
        total_time =        start_time

        # for each Station
        for station in Station.objects.all():

            print ''
            print station

            # find all connected station data
            # is properly ordered by 1. year 2. station (ascending)
            t=time.time()
            station_data = StationData.objects.filter(station=station)
            print "1", time.time()-t

            t=time.time()
            # find min and max year
            min_year = station_data.aggregate(Min('year'))['year__min']
            max_year = station_data.aggregate(Max('year'))['year__max']

            # get total number of months that lack either temp or prcp data
            missing_months = station_data.filter(is_complete=False)

            # get percentage of complete months
            num_months = station_data.count()
            num_missing_months = missing_months.count()
            complete_data_rate = float(num_months-num_missing_months) / float(num_months)

            # identify gaps = consecutive missing months
            gaps = [0]*(MAX_GAP+1)      # final list: number of gaps per gap size
            largest_gap = 0             # largest gap found so far
            currently_in_gap = False    # currently in a gap
            curr_gap_size = 0           # size of current gap
            station_data_it = 0         # iterator in station data array
            num_station_data = station_data.count()     # number of data points
            print "2", time.time()-t

            t1 = []
            t2 = []

            ## for each year
            year = min_year
            while year <= max_year:

                ## for each month
                month = 1
                while month <= NUM_MONTHS:

                    t=time.time()
                    ## is it a gap? (default: yes)
                    is_gap = True

                    ## check if it is NOT a gap, i.e. check if data is available
                    ## 1) iterator / index is in range
                    if  (station_data_it <= num_station_data):
                        this_station_data = station_data[station_data_it]

                        ## 2) this particular combination year+month exists
                        if  (this_station_data.year is year) and \
                            (this_station_data.month is month):

                            ## 3) station data is complete => no gap
                            if (this_station_data.is_complete):
                                is_gap = False

                            ## => iterate to next station data point
                            station_data_it += 1

                    ## in other cases: data either not available or incomplete
                    ## => it is a gap

                    t1.append(time.time()-t)
                    t=time.time()

                    ## if it is a gap, count the gap size. 4 cases:
                    if currently_in_gap:

                        ## 1) currently in a gap and gap continues => increment!
                        if is_gap:
                            gap += 1

                        ## 2) currently in a gap and gap ended => finalize!
                        ## -> gap size n has one more occurence
                        else:
                            gaps[gap] += 1
                            largest_gap = max(largest_gap, gap)
                            gap = 0
                            currently_in_gap = False

                    else:

                        ## 3) currently not in a gap and gap found => start gap
                        if is_gap:
                            gap = 1
                            currently_in_gap = True

                        ## 4) currently not in a gap and no gap found => continue!
                        else: pass

                    t2.append(time.time()-t)

                    ## next month
                    month += 1

                ## next year
                year += 1

            # finalize last gap
            if currently_in_gap:
                gaps[gap] += 1
                largest_gap = max(largest_gap, gap)
                gap = 0
                currently_in_gap = False

            print "3", sum(t1)
            print "4", sum(t2)

            # finally write the data
            print min_year, max_year, num_missing_months, complete_data_rate, largest_gap
            station.min_year =              min_year
            station.max_year =              max_year
            station.missing_months =        num_missing_months
            station.complete_data_rate =    complete_data_rate
            station.largest_gap =           largest_gap
            station.save()

            # session and time management
            station_ctr += 1
            if station_ctr % BULK_SIZE == 0:
                transaction.commit()
                print_time_statistics('stations', station_ctr, start_time, intermediate_time)
                intermediate_time = time.time()

                if TEST_RUN: return

        # finalize
        transaction.commit()
        print 'FINISHED UPDATING DATABASE'
        print_time_statistics('stations', station_ctr, start_time)
        print ''

        # cleanup: manual database commits in bulks
        transaction.set_autocommit(True)
