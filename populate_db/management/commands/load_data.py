################################################################################
# POPULATE THE CLIMATE DATABASE WITH WEATHER STATIONS DATA
################################################################################

# execute me using:
# python manage.py load_data <option>
# <option> =
#   A = populate everything (station -> temp -> prcp)
#   S = populate only stations (N.B: deletes temp and prcp data!)
#   T = (re)populate only temperature
#   P = (re)populate only precipitation

################################################################################
# GLOBAL CONSTANTS
################################################################################

POSSIBLE_ARGUMENTS = \
[
    'A', 'a',   # all data
    'S', 's',   # only stations
    'T', 't',   # only temperature data
    'P', 'p'    # only precipitation
]


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

# own modules
from populate_db.models import *
from populate_db.management.commands.input_data import *
from populate_db.management.commands.helpers import *


################################################################################
# MAIN
################################################################################

class Command(BaseCommand):
    help = "Populates the database with initial data. Three options \
            A = populate everything (station -> temp -> prcp) \
            S = populate only stations (N.B: deletes temp and prcp data!) \
            T = (re)populate only temperature \
            P = (re)populate only precipitation"


    # ==========================================================================
    # Handle additional populate options given to the command
    # ==========================================================================

    def add_arguments(self, parser):
        # poption = populate_option :-D
        parser.add_argument('poption', type=str, default=False)


    # ==========================================================================
    # MAIN
    # ==========================================================================

    def handle(self, *args, **options):

        # get name of poption to be filled
        # A = all, T = temperature, P = precipitation
        poption = options['poption']

        # test: is poption correct?
        if poption not in POSSIBLE_ARGUMENTS:
            print 'The argument you have given is not supported'
            print 'Please add one of the following: ' \
                    + (', '.join(POSSIBLE_ARGUMENTS))
            return

        # speedup: manual database commits in bulks
        transaction.set_autocommit(False)

        # cleanup
        num_station_data = StationData.objects.count()
        if (poption == 'T') or (poption == 'P'):
            station_data = StationData.objects.all()
            cleanup_ctr = 0
            for data in station_data:
                if poption == 'T':
                    data.temperature = None
                else: # poption == 'P'
                    data.precipitation = None
                data.is_complete = False
                data.save()
                cleanup_ctr += 1
                if cleanup_ctr % BULK_SIZE == 0:
                    transaction.commit()
                    print\
                    (
                        str(cleanup_ctr).rjust(8)
                        + ' records cleaned ('
                        + str('%05.2f' % (100*float(cleanup_ctr)/float(num_station_data)))
                        + ' %)'
                    )
            transaction.commit()

        else: # poption == 'A' or 'S':
            Station.objects.all().delete()
            # also automatically deletes StationData!

        print 'FINISHED CLEANING DATABASE\n'

        # populate
        if poption == 'T':
            self.populate_data('temperature')
        elif poption == 'P':
            self.populate_data('precipitation')
        elif poption == 'S':
            self.populate_stations()
        else: # poption == 'A'
            self.populate_stations()
            self.populate_data('temperature')
            self.populate_data('precipitation')

        # cleanup: manual database commits in bulks
        transaction.set_autocommit(True)


    # ==========================================================================
    # Populate database with weather stations
    # ==========================================================================

    def populate_stations(self):

        # COUNTRY CODES

        country_codes = {}

        with open(get_file(COUNTRY_CODES['path'])) as in_file:
            for line in in_file:
                code = get_int \
                (
                    line,
                    COUNTRY_CODES['characters']['code']
                )
                country = get_string \
                (
                    line,
                    COUNTRY_CODES['characters']['country']
                ).title()
                country_codes[code] = country


        # preparation for time management
        station_ctr =       0
        start_time =        time.time()
        intermediate_time = start_time
        total_time =        start_time


        # read all weather stations and write them into the database
        for dataset in DATASETS:

            stations = DATASETS[dataset]['stations']

            # for each weather station in file
            with open(get_file(stations['path'])) as in_file:

                for line in in_file:

                    id = get_int \
                    (
                        line,
                        stations['characters']['station_id']
                    )

                    lat = get_float \
                    (
                        line,
                        stations['characters']['lat'],
                        2
                    )

                    lng = get_float \
                    (
                        line,
                        stations['characters']['lng'],
                        2
                    )

                    elev = get_int \
                    (
                        line,
                        stations['characters']['elv'],
                    )

                    name = get_station_name \
                    (
                        line,
                        stations['characters']['name']
                    )

                    # data value check: elevation given?
                    for null_value in stations['null_values']:
                        if str(elev) == null_value:
                            elev = None

                    # get country name from country code
                    country = country_codes.get(int(str(id)[0:3]))

                    # test if station id is already registered in the database
                    existing_station = Station.objects.filter(id=id)
                    if existing_station.exists():
                        pass # ignore for now

                    # entry does not exist so far -> create it!
                    else:
                        new_station = Station \
                        (
                            id =        id,
                            name =      name,
                            country =   country,
                            lat =       lat,
                            lng =       lng,
                            elev =      elev,
                        )
                        new_station.save()

                        station_ctr += 1
                        if station_ctr % BULK_SIZE == 0:
                            transaction.commit()
                            print_time_statistics('saved', 'stations',\
                                station_ctr, start_time, intermediate_time)
                            intermediate_time = time.time()

        transaction.commit()
        print '\nFINISHED WRITING STATIONS TO DATABASE'
        print_time_statistics('saved', 'stations', station_ctr, start_time)
        print ''


    # ==========================================================================
    # Populate database with data from precipitation or temperature dataset
    # ==========================================================================

    def populate_data(self, dataset):

        input_data = DATASETS[dataset]['data']

        # preparation for time measurement and
        record_ctr =        0
        start_time =        time.time()
        intermediate_time = start_time
        total_time =        start_time

        # for each data record in dataset
        with open(get_file(input_data['path'])) as in_file:
            for line in in_file:
                station_id = get_int \
                (
                    line,
                    input_data['characters']['station_id']
                )
                year = get_int \
                (
                    line,
                    input_data['characters']['year']
                )

                # get data for each month
                monthly_data = [None]   # skip idx [0] => data starts at [1]
                i = 1
                while i <= NUM_MONTHS:

                    # assemble month string '1', '2', ... , '12'
                    month_str = str(i)

                    # get raw data
                    this_month_value = get_int \
                    (
                        line,
                        input_data['characters'][month_str]
                    )

                    # if data has the null value, actually write null
                    is_null = False
                    for null_value in input_data['null_values']:
                        if str(this_month_value) == null_value:
                            monthly_data.append(None)
                            is_null = True

                    # else: divide value by divison factor in data
                    # (converts int to float)
                    if not is_null:
                        monthly_data.append \
                        (
                            float(this_month_value) / input_data['division_factor']
                        )

                    # next month
                    i += 1

                # get foreign key: station
                try:
                    station = Station.objects.get(id=station_id)

                except:
                    print "Related station could not be found"
                    continue

                # for each month
                for month, value in enumerate(monthly_data):

                    # ignore None (0. month)
                    if value is None:
                        continue

                    # check if object (station->year->month) exists
                    try:
                        station_data = StationData.objects.get \
                        (
                            station=station,
                            year=year,
                            month=month
                        )
                    # if it does not exist, create it
                    except StationData.DoesNotExist:
                        station_data = StationData \
                        (
                            station=station,
                            year=year,
                            month=month
                        )

                    # update value for temperature / precipitation
                    if dataset == 'temperature':
                        station_data.temperature = value

                    elif dataset == 'precipitation':
                        station_data.precipitation = value

                    # reset is_complete flag
                    if  (station_data.temperature is None) or \
                        (station_data.precipitation is None):
                        station_data.is_complete = False
                    else:
                        station_data.is_complete = True

                    # done!
                    station_data.save()

                    # go to next data
                    record_ctr += 1

                    # save each bulk with BULK_SIZE to the database
                    if record_ctr % BULK_SIZE == 0:
                        transaction.commit()
                        print_time_statistics \
                        (
                            dataset + ' data',
                            record_ctr,
                            start_time,
                            intermediate_time
                        )
                        intermediate_time = time.time()

        # finalize database writing
        transaction.commit()
        print '\nFINISHED WRITING ' + dataset.upper() + ' TO DATABASE'
        print_time_statistics \
        (
            dataset + ' data',
            record_ctr,
            start_time
        )
        print '\n\n'
