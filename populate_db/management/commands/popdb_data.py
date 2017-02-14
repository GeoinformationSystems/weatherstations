################################################################################
# POPULATE THE CLIMATE DATABASE WITH HISTORICAL TEMPERATURE DATA
################################################################################

# execute me using:
# python manage.py popdb_temperature <dataset>
# <dataset> = temperature or precipitation

################################################################################
# GLOBAL CONSTANTS
################################################################################

BULK_SIZE = 1000
NUM_MONTHS = 12


################################################################################
# INCLUDES
################################################################################

# general python modules
import os
import time
import importlib # try around with getattrib to call function from string

# django modules
from django.core.management.base import BaseCommand, CommandError, NoArgsCommand
from django.conf import settings
from django.db import models, transaction

# own modules
from populate_db.models import *
from populate_db.management.commands.input_data import *
from populate_db.management.commands.helpers import *


################################################################################
# MAIN
################################################################################

class Command(BaseCommand):
    help = 'populates the database with initial data for either temperature \
            or precipitation. Call the '

    def add_arguments(self, parser):
        parser.add_argument('dataset', type=str, default=False)

    def handle(self, *args, **options):

        # get name of dataset to be filled (temperature or precipitation)
        dataset = ''
        for val in INPUT_FILES:
            try:    # check only datasets with have argument alternatives
                for alternative in INPUT_FILES[val]['argument_alternatives']:
                    if alternative == options['dataset']:
                        dataset = val
                        break
            except: pass

        if dataset == '':
            print "Dataset could not be found:"
            print "Specify 'T' for the temperature or 'P' for the precipitation dataset"
            return

        # speedup: manual database commits in bulks
        transaction.set_autocommit(False)

        # cleanup
        if dataset == 'temperature':
            TemperatureData.objects.all().delete()
        elif dataset == 'precipitation':
            PrecipitationData.objects.all().delete()

        # preparation for time measurement and
        record_ctr =        0
        start_time =        time.time()
        intermediate_time = start_time
        total_time =        start_time

        # for each data record in dataset
        with open(get_file(INPUT_FILES[dataset]['data']['path'])) as in_file:
            for line in in_file:
                station_id = get_int(
                    line,
                    INPUT_FILES[dataset]['data']['characters']['station_id']
                )
                year = get_int(
                    line,
                    INPUT_FILES[dataset]['data']['characters']['year']
                )

                # get data for each month
                monthly_data = [None]   # skip idx [0] => data starts at [1]
                i = 1
                while i <= NUM_MONTHS:

                    # assemble month string 'm01', 'm02', ... , 'm12'
                    m_str = 'm'
                    if i < 10:
                        m_str += '0'
                    m_str += str(i)

                    # get raw data
                    this_month_value = get_int(
                        line,
                        INPUT_FILES[dataset]['data']['characters'][m_str]
                    )

                    # if data has the null value, actually write null
                    if str(this_month_value) == (INPUT_FILES[dataset]['data']['null_value']):
                        monthly_data.append(None)

                    # else: divide value by divison factor in data
                    # (converts int to float)
                    else:
                        monthly_data.append(
                            float(this_month_value) / INPUT_FILES[dataset]['data']['division_factor']
                        )

                    # next month
                    i += 1

                # get foreign key: station
                try:
                    station = Station.objects.get(id=station_id)

                except DoesNotExist:
                    print "Related station could not be found"
                    continue

                # related station found => save data to database
                if dataset == 'temperature':
                    new_data = TemperatureData(
                        station =   station,
                        year =      year,
                        m01 =       monthly_data[ 1],
                        m02 =       monthly_data[ 2],
                        m03 =       monthly_data[ 3],
                        m04 =       monthly_data[ 4],
                        m05 =       monthly_data[ 5],
                        m06 =       monthly_data[ 6],
                        m07 =       monthly_data[ 7],
                        m08 =       monthly_data[ 8],
                        m09 =       monthly_data[ 9],
                        m10 =       monthly_data[10],
                        m11 =       monthly_data[11],
                        m12 =       monthly_data[12],
                    )
                elif dataset == 'precipitation':
                    new_data = PrecipitationData(
                        station =   station,
                        year =      year,
                        m01 =       monthly_data[ 1],
                        m02 =       monthly_data[ 2],
                        m03 =       monthly_data[ 3],
                        m04 =       monthly_data[ 4],
                        m05 =       monthly_data[ 5],
                        m06 =       monthly_data[ 6],
                        m07 =       monthly_data[ 7],
                        m08 =       monthly_data[ 8],
                        m09 =       monthly_data[ 9],
                        m10 =       monthly_data[10],
                        m11 =       monthly_data[11],
                        m12 =       monthly_data[12],
                    )
                new_data.save()

                # go to next data
                record_ctr += 1

                # save each bulk with BULK_SIZE to the database
                if record_ctr % BULK_SIZE == 0:
                    transaction.commit()
                    print_time_statistics('records', record_ctr, start_time, intermediate_time)
                    intermediate_time = time.time()

        transaction.commit()
        print 'FINISHED WRITING STATIONS TO DATABASE'
        print_time_statistics('records', record_ctr, start_time)

        # cleanup
        transaction.set_autocommit(True)
