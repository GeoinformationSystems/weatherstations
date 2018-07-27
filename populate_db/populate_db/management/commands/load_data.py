################################################################################
# INCLUDES
################################################################################

# general python modules
from haversine import haversine
from itertools import islice
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# django modules
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.gis.geos import Point

# own modules
from populate_db.models import *
from populate_db.management.commands.helpers import *
from input_data import *

################################################################################
# POPULATE THE CLIMATE DATABASE WITH WEATHER STATIONS DATA
################################################################################

# execute me using:
# python manage.py load_data <option>
# <option> =
#   A = populate everything (station -> temp -> prcp)
#   S = populate only stations (N.B: deletes temp and prcp data!)
#   D = (re)populate temperature and preciptation data

################################################################################
# GLOBAL CONSTANTS
################################################################################

POSSIBLE_ARGUMENTS = \
    [
        'A', 'a',  # all data
        'S', 's',  # only stations
        'D', 'd'  # (re)populate temperature and preciptation
    ]

# maximum distance between two stations with the same id
# to say that they are "the same" / have only slightly moved
DISTANCE_THRESHOLD = 2.0  # [km]

TEST_RUN = False


################################################################################
# MAIN
################################################################################

class Command(BaseCommand):
    help = "Populates the database with initial data. Three options \
            A = populate everything (station -> temp -> prcp) \
            S = populate only stations (N.B: deletes temp and prcp data!) \
            D = (re)populate temperature and precipitation data"

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
        if str.upper(poption) == 'D':
            print 'Deleting all ' + str(StationData.objects.count()) + ' StationData objects ... \n'
            StationData.objects.all().delete()
        else:  # poption == 'A' or 'S':
            print 'Deleting all ' + str(Station.objects.count()) + ' Station objects (and data) ... \n'
            Station.objects.all().delete()
            # also automatically deletes StationData!
        transaction.commit()
        print 'FINISHED CLEANING DATABASE\n'

        # populate
        if str.upper(poption) == 'S':
            self.populate_stations()
        elif str.upper(poption) == 'D':
            self.populate_data()
        else:  # poption == 'A'
            self.populate_stations()
            self.populate_data()

    # ==========================================================================
    # Populate database with weather stations
    # ==========================================================================

    def populate_stations(self):

        # COUNTRY CODES
        # -------------
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

        # INITIAL STATION POPULATION
        # --------------------------

        # preparation for time management
        station_ctr = 0
        start_time = time.time()
        intermediate_time = start_time
        total_time = start_time

        # read all weather stations and write them into the database
        for dataset in DATASETS:

            stations = DATASETS[dataset]['stations']

            # for each weather station in file
            with open(get_file(stations['path'])) as in_file:

                for line in islice(in_file, None):

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

                    # geom transformation
                    geom = Point(lng, lat)

                    # save new station
                    new_station = Station(
                        id=id,
                        name=name,
                        country=country,
                        lat=lat,
                        lng=lng,
                        geom=geom,
                        elev=elev,
                    )
                    new_station.save()

                    station_ctr += 1

                    if station_ctr % BULK_SIZE == 0:
                        transaction.commit()
                        print_time_statistics('saved', 'stations', station_ctr, start_time, intermediate_time)
                        intermediate_time = time.time()

        transaction.commit()
        print '\nFINISHED WRITING STATIONS TO DATABASE'
        print_time_statistics('saved', 'stations', station_ctr, start_time)
        print ''

        # MERGE DUPLICATES
        # ----------------

        # preparation for time management
        duplicate_ctr = 0
        start_time = time.time()
        intermediate_time = start_time
        total_time = start_time

        # get all countries which have stations
        # use a set to avoid duplicates
        countries = set()
        for station in Station.objects.all():
            countries.add(station.country)

        # strategy: first identify all duplicates, then update/delete them
        # => avoids manual iterator resetting helll
        duplicates = []

        # find all duplicates
        for country in countries:

            # get all stations in this country
            stations_in_country = Station.objects.filter(country=country)

            # find duplicates (O(n*n))
            i = 0
            j = 1
            end = len(stations_in_country) - 1

            while i < end:
                j = i + 1
                while j < end:

                    # get stations
                    a = stations_in_country[i]
                    b = stations_in_country[j]

                    # check if first 8 digits of id are the same
                    # -> because last three digits might be increments of
                    #    the same station that has moved or so...
                    if str(a.id)[0:7] == str(b.id)[0:7]:

                        # check if the distance between both stations is small
                        # -> because it could be the station has slightly moved
                        a_coords = (a.lat, a.lng)
                        b_coords = (b.lat, b.lng)
                        stations_close = haversine(a_coords, b_coords) < DISTANCE_THRESHOLD

                        # check if the names are the same and not empty
                        names_same = (a.name == b.name) and (a.name != '')
                        if names_same or stations_close:

                            # duplicate found! => merge stations
                            # assumption: A = master, B = duplicate
                            # N.B! A master station can have multiple duplicates

                            # find position in duplicate list where to append it
                            # default: None => append new duplicate
                            duplicates_idx = None

                            # if master already has duplicates, use this idx
                            for idx, duplicate in enumerate(duplicates):
                                for alternative in duplicate:
                                    if alternative == a or alternative == b:
                                        duplicates_idx = idx

                            # create new set of duplicates
                            if not duplicates_idx:
                                duplicates.append(set())
                                duplicates_idx = len(duplicates) - 1

                            # finally add duplicates
                            duplicates[duplicates_idx].add(a)
                            duplicates[duplicates_idx].add(b)

                            duplicate_ctr += 1
                            if duplicate_ctr % (BULK_SIZE / 10) == 0:
                                print_time_statistics('found', 'duplicates', duplicate_ctr, start_time,
                                                      intermediate_time)
                                intermediate_time = time.time()

                    # check next station
                    j += 1
                i += 1

        print '\nFINISHED IDENTIFYING DUPLICATES IN DATABASE'
        print_time_statistics('found', 'duplicates', duplicate_ctr, start_time)
        print ''

        # handle duplicates
        duplicate_ctr = 0
        start_time = time.time()
        intermediate_time = start_time
        total_time = start_time

        for duplicate in duplicates:

            # convert set to list
            station_duplicates = list(duplicate)

            # assumption:
            # first station is the master, the other stations are duplicates
            master = station_duplicates[0]

            # for each duplicate:
            # create StationDuplicates and delete itself
            i = 1  # skip the master!
            end = len(station_duplicates)
            while i < end:
                new_duplicate = StationDuplicate(
                    master_station=master,
                    duplicate_station=station_duplicates[i].id
                    # -> id, not object itself, since it will be deleted
                )
                new_duplicate.save()
                # station_duplicates[i].delete()
                station_duplicates[i].original = False
                station_duplicates[i].save()

                duplicate_ctr += 1
                if duplicate_ctr % BULK_SIZE == 0:
                    transaction.commit()
                    print_time_statistics('removed', 'station duplicates', duplicate_ctr, start_time, intermediate_time)
                    intermediate_time = time.time()

                # go to next station duplicate
                i += 1

        transaction.commit()
        print '\nFINISHED REMOVING STATION DUPLICATES FROM DATABASE'
        print_time_statistics('removed', 'station duplicates', duplicate_ctr, start_time)
        print ''

    # ==========================================================================
    # Populate database with data from precipitation or temperature dataset
    # ==========================================================================
    def populate_data(self):

        # preparation for time measurement and
        record_ctr = 0
        start_time = time.time()
        intermediate_time = start_time

        # connection to postgres database
        stationsdata_db = create_engine('postgresql://postgres:postgres@localhost:5432/climatecharts_weatherstations')

        # read temperature file into dataframe
        st = self.get_dataframe_from_data('temperature')
        print_time_statistics('have read temperature data', '', record_ctr, start_time, intermediate_time)
        intermediate_time = time.time()

        # read precipitation file into dataframe
        sp = self.get_dataframe_from_data('precipitation')
        print_time_statistics('have read precipitation data', '', record_ctr, start_time, intermediate_time)
        intermediate_time = time.time()

        # join temperature and precipitation dataframes
        df = pd.concat([st, sp], axis=1)
        print_time_statistics('concated dataframe', '', record_ctr, start_time, intermediate_time)
        intermediate_time = time.time()

        # calculate new colum with boolean if temperature & precipitation is available for this dataset
        df['is_complete'] = df.apply(lambda row: self.row_complete(row), axis=1)
        print_time_statistics('new column added', '', record_ctr, start_time, intermediate_time)
        intermediate_time = time.time()

        # write results into database
        df.to_sql('populate_db_stationdata', stationsdata_db, if_exists='append', index=True, chunksize=BULK_SIZE * 10)
        print_time_statistics('FINISHED WRITING populate_db_stationdata TO DATABASE', '', record_ctr, start_time,
                              intermediate_time)
        intermediate_time = time.time()

        # handle duplicates
        duplicate_ctr = 0
        stationdata_notfound_ctr = 0
        multiple_stationdata_found_ctr = 0
        #
        # sort out all duplicate stations data and merge with master station
        for duplicate_station in StationDuplicate.objects.all():
            try:
                for duplicate_station_data in StationData.objects.filter(station=duplicate_station.duplicate_station):
                    try:
                        master_station_data = StationData.objects.get(station=duplicate_station_data.station,
                                                                      year=duplicate_station_data.year,
                                                                      month=duplicate_station_data.month)
                        # save only data from duplicate station if in master station is nothing saved yet
                        if master_station_data.temperature is None:
                            master_station_data.temperature = duplicate_station_data.temperature
                        if master_station_data.precipitation is None:
                            master_station_data.precipitation = duplicate_station_data.precipitation
                        master_station_data.save()
                        duplicate_station_data.delete()

                        duplicate_ctr += 1
                        if duplicate_ctr % BULK_SIZE == 0:
                            transaction.commit()
                            print_time_statistics('merged and removed', 'data duplicates', duplicate_ctr, start_time,
                                                  intermediate_time)
                            intermediate_time = time.time()
                    except StationData.MultipleObjectsReturned:
                        multiple_stationdata_found_ctr += 1
                        print 'found multiple objects for ' + duplicate_station_data
            except StationData.DoesNotExist:
                stationdata_notfound_ctr += 1
                print 'found no Station Data object for ' + duplicate_station

        transaction.commit()
        print '\nFINISHED REMOVING DATA DUPLICATES FROM DATABASE'
        print_time_statistics('\tin total merged and removed', 'data duplicates', duplicate_ctr, intermediate_time)
        print_time_statistics('\tin total number of StationData not matchable: ', '', stationdata_notfound_ctr,
                              intermediate_time)
        print_time_statistics('\tin total number of Multiple StationData errors: ', '', multiple_stationdata_found_ctr,
                              intermediate_time)

    def get_dataframe_from_data(self, dataset):
        input_data = DATASETS[dataset]['data']

        # create names and column specification for pandas fwf function
        colspecs = []
        names = []
        for columns in input_data['pandas_characters']:
            colspecs.append(input_data['pandas_characters'][columns])
            names.append(columns)

        nrows = 50000 if TEST_RUN else None

        # pandas fwf can read and process large files very quickly and store it into a dataframe
        fwf = pd.read_fwf(filepath_or_buffer=input_data['path'], colspecs=colspecs,
                          delim_whitespace=True, header=None, names=names, index_col=[0, 1], nrows=nrows)

        # bring dataframe in the right shape and convert it to a series
        fwf.columns.name = 'month'
        series = fwf.stack()
        series.name = dataset
        series.reset_index()

        # replace null values
        for null_value in input_data['null_values']:
            series.replace(to_replace=int(null_value), value=np.nan, inplace=True)

        # apply the division factor on the series values
        series = series.apply(lambda x: x / input_data['division_factor'])
        return series

    # if temperature and precipitation is null the row is complete
    def row_complete(self, row):
        if np.isnan(row['temperature']) or np.isnan(row['precipitation']):
            return False
        else:
            return True
