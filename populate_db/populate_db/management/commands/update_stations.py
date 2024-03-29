################################################################################
# INCLUDES
################################################################################

# general python modules

# django modules
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import *

# own modules
from populate_db.models import Station, StationData, StationDuplicate
from populate_db.management.commands.helpers import *
from populate_db.management.commands.input_data import *

################################################################################
# UPDATE THE CLIMATE DATABASE (STATIONS) WITH STATISTICALLY RELEVANT DATA
################################################################################

# execute me using:
# python manage.py update_stations


################################################################################
# GLOBAL CONSTANTS
################################################################################

# check only limited set of data
TEST_RUN = False


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
        station_ctr = 0
        start_time = time.time()
        intermediate_time = start_time
        deactivated_ctr = 0
        # total_time = start_time

        # for each Station
        for station in Station.objects.all():

            # find all connected station data
            # is properly ordered by 1. year 2. station (ascending)
            station_datas = StationData.objects.filter(station=station)

            # find min and max year
            min_year = station_datas.aggregate(Min('year'))['year__min']
            max_year = station_datas.aggregate(Max('year'))['year__max']

            if min_year is None:
                min_year = 0
            if max_year is None:
                max_year = 0

            # get total number of months that lack either temp or prcp data
            missing_months = station_datas.filter(is_complete=False)

            # get percentage of complete months
            num_months = station_datas.count()
            num_missing_months = missing_months.count()
            if num_months != num_missing_months:
                complete_data_rate = float(num_months - num_missing_months) / float(num_months)
            else:
                complete_data_rate = 0

            # identify gaps = consecutive missing months
            gaps = [0] * (MAX_GAP + 1)  # final list: number of gaps per gap size
            gap = 0
            largest_gap = 0  # largest gap found so far
            currently_in_gap = False  # currently in a gap
            curr_gap_size = 0  # size of current gap

            # create consecutive list of monthly data: is data complete?
            # structure: [min_year/Jan, min_year/Feb, ..., max_yar/Dec]
            monthly_completion_list = [0] * ((max_year - min_year + 1) * NUM_MONTHS)

            # for each station data point
            for station_data in station_datas:
                # get index for monthly_completion_list
                idx = ((station_data.year - min_year) * NUM_MONTHS) + station_data.month - 1

                # add information to list: is data point complete?
                monthly_completion_list[idx] = station_data.is_complete

            # for each monthly completion data value (= is it a gap?)
            for month_complete in monthly_completion_list:

                # if it is a gap, count the gap size. 4 cases:
                if currently_in_gap:

                    # 1) currently in a gap and gap continues => increment!
                    if not month_complete:
                        gap += 1

                    # 2) currently in a gap and gap ended => finalize!
                    # -> gap size n has one more occurence
                    else:
                        gaps[gap] += 1
                        largest_gap = max(largest_gap, gap)
                        gap = 0
                        currently_in_gap = False

                else:

                    # 3) currently not in a gap and gap found => start gap
                    if not month_complete:
                        gap = 1
                        currently_in_gap = True

                    # 4) currently not in a gap and no gap found => continue!
                    else:
                        pass

            # finalize last gap
            if currently_in_gap:
                gaps[gap] += 1
                largest_gap = max(largest_gap, gap)
                gap = 0
                currently_in_gap = False

            # finally write the data
            station.min_year = min_year
            station.max_year = max_year
            station.missing_months = num_missing_months
            station.complete_data_rate = complete_data_rate
            station.largest_gap = largest_gap
            if complete_data_rate == 0.0:
                deactivated_ctr += 1
            station.save()

            # session and time management
            station_ctr += 1
            if station_ctr % BULK_SIZE == 0:
                transaction.commit()
                print_time_statistics('updated', 'stations', station_ctr, start_time, intermediate_time)
                intermediate_time = time.time()

                # if TEST_RUN: return

        # finalize
        transaction.commit()
        print ('FINISHED UPDATING DATABASE')
        print_time_statistics('in total updated', 'stations', station_ctr, start_time)
        print_time_statistics('in total deactivated', 'stations', deactivated_ctr, start_time)
        print ('')

        # data cleanup: delete all stations that have 0.0 coverage
        # Station.objects.filter(complete_data_rate=0.0).delete()

        # cleanup: manual database commits in bulks
        # transaction.set_autocommit(True)
