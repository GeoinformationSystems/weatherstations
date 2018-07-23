################################################################################
# INCLUDES
################################################################################

# general python modules
from haversine import haversine

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
#   T = (re)populate only temperature
#   P = (re)populate only precipitation

################################################################################
# GLOBAL CONSTANTS
################################################################################

POSSIBLE_ARGUMENTS = \
    [
        'A', 'a',  # all data
        'S', 's',  # only stations
        'T', 't',  # only temperature data
        'P', 'p'  # only precipitation
    ]

# maximum distance between two stations with the same id
# to say that they are "the same" / have only slightly moved
DISTANCE_THRESHOLD = 2.0  # [km]

TEST_RUN = True


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
        if (str.upper(poption) == 'T') or (str.upper(poption) == 'P'):
            station_data = StationData.objects.all()
            cleanup_ctr = 0
            for data in station_data:
                if str.upper(poption) == 'T':
                    data.temperature = None
                else:  # poption == 'P'
                    data.precipitation = None
                data.is_complete = False
                data.save()
                cleanup_ctr += 1
                if cleanup_ctr % BULK_SIZE == 0:
                    transaction.commit()
                    print \
                        (
                                str(cleanup_ctr).rjust(8)
                                + ' records cleaned ('
                                + str('%05.2f' % (100 * float(cleanup_ctr) / float(num_station_data)))
                                + ' %)'
                        )
            transaction.commit()

        else:  # poption == 'A' or 'S':
            Station.objects.all().delete()
            # also automatically deletes StationData!

        print 'FINISHED CLEANING DATABASE\n'

        # populate
        if str.upper(poption) == 'T':
            self.populate_data('temperature')
        elif str.upper(poption) == 'P':
            self.populate_data('precipitation')
        elif str.upper(poption) == 'S':
            self.populate_stations()
        else:  # poption == 'A'
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
                station_duplicates[i].delete()

                duplicate_ctr += 1
                if duplicate_ctr % BULK_SIZE == 0:
                    transaction.commit()
                    print_time_statistics('removed', 'duplicates', duplicate_ctr, start_time, intermediate_time)
                    intermediate_time = time.time()

                # go to next station duplicate
                i += 1

        transaction.commit()
        print '\nFINISHED REMOVING DUPLICATES FROM DATABASE'
        print_time_statistics('removed', 'duplicates', duplicate_ctr, start_time)
        print ''

    # ==========================================================================
    # Populate database with data from precipitation or temperature dataset
    # ==========================================================================

    def populate_data(self, dataset):

        # get reference to input dataset
        input_data = DATASETS[dataset]['data']

        # preparation for time measurement and
        record_ctr = 0
        start_time = time.time()
        intermediate_time = start_time
        total_time = start_time

        # for each data record in dataset
        with open(get_file(input_data['path'])) as in_file:
            for line in in_file:
                station_id = get_int(
                    line,
                    input_data['characters']['station_id']
                )
                year = get_int(
                    line,
                    input_data['characters']['year']
                )

                # get data for each month
                monthly_data = [None]  # skip idx [0] => data starts at [1]
                i = 1
                while i <= NUM_MONTHS:

                    # assemble month string '1', '2', ... , '12'
                    month_str = str(i)

                    # get raw data
                    this_month_value = get_int(
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
                        monthly_data.append(
                            float(this_month_value) / input_data['division_factor']
                        )

                    # next month
                    i += 1

                # get related station:
                # 1) check in station duplicates
                try:
                    duplicate = StationDuplicate.objects.get(duplicate_station=station_id)
                    station = duplicate.master_station

                except:

                    # 2) check in (master) stations
                    try:
                        station = Station.objects.get(id=station_id)

                    except:
                        print "Related station with id", id, "could not be  found"
                        continue

                # for each month
                for month, value in enumerate(monthly_data):

                    # ignore 0. month
                    if value is None: continue

                    # check if object (station->year->month) exists
                    try:
                        station_data = StationData.objects.get(
                            station=station,
                            year=year,
                            month=month
                        )
                    # if it does not exist, create it
                    except StationData.DoesNotExist:
                        station_data = StationData(
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
                    if (station_data.temperature is None) or (station_data.precipitation is None):
                        station_data.is_complete = False
                    else:
                        station_data.is_complete = True

                    # done!
                    station_data.save()

                    # go to next data
                    record_ctr += 1

                    # save each bulk to the database
                    if record_ctr % BULK_SIZE == 0:
                        transaction.commit()
                        print_time_statistics('saved', dataset + ' data', record_ctr, start_time, intermediate_time)
                        intermediate_time = time.time()

        # finalize database writing
        transaction.commit()
        print '\nFINISHED WRITING ' + dataset.upper() + ' TO DATABASE'
        print_time_statistics('saved', dataset + ' data', record_ctr, start_time)
        print '\n\n'
