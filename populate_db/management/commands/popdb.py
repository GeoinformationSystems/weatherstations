################################################################################
# POPULATE THE CLIMATE DATABASE WITH WEATHER STATIONS DATA
################################################################################

# execute me using:
# python manage.py popdb <option>
# <option> =
#   A = populate everything (station -> temp -> prcp)
#   S = populate only stations (N.B: deletes temp and prcp data!)
#   T = (re)populate only temperature
#   P = (re)populate only precipitation

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

        # speedup: manual database commits in bulks
        transaction.set_autocommit(False)

        # cleanup
        if poption == 'T':
            station_data = StationData.objects.all()
            for data in station_data:
                data.temperature = None
        elif poption == 'P':
            station_data = StationData.objects.all()
            for data in station_data:
                data.precipitation = None
        else: # poption == 'A' or 'S':
            Station.objects.all().delete()

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


    # ==========================================================================
    # Populate database with weather stations
    # ==========================================================================

    def populate_stations(self):

        # COUNTRY CODES

        country_codes = {}

        with open(get_file(COUNTRY_CODES['path'])) as in_file:
            for line in in_file:
                code = get_int(
                    line,
                    COUNTRY_CODES['characters']['code']
                )
                country = get_string(
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
                    id = get_int(
                        line,
                        stations['characters']['station_id']
                    )
                    lat = get_float(
                        line,
                        stations['characters']['lat'],
                        2
                    )
                    lng = get_float(
                        line,
                        stations['characters']['lng'],
                        2
                    )
                    elev = get_int(
                        line,
                        stations['characters']['elv'],
                    )
                    name = get_station_name(
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
                        new_station = Station(
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
                            print_time_statistics('stations', station_ctr, start_time, intermediate_time)
                            intermediate_time = time.time()

        transaction.commit()
        print 'FINISHED WRITING STATIONS TO DATABASE'
        print_time_statistics('stations', station_ctr, start_time)

        # cleanup
        transaction.set_autocommit(True)


    # ==========================================================================
    # Populate database with data from precipitation or temperature dataset
    # ==========================================================================

    def populate_data(self, dataset):

        input_data = DATASETS[dataset]['data']

        # todo: integrate from popdb_data
