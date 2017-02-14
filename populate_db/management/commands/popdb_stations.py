################################################################################
# POPULATE THE CLIMATE DATABASE WITH WEATHER STATIONS DATA
################################################################################

# execute me using:
# python manage.py popdb_temperature

################################################################################
# GLOBAL CONSTANTS
################################################################################

BULK_SIZE = 1000


################################################################################
# INCLUDES
################################################################################

# general python modules
import os
import time

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

class Command(NoArgsCommand):
    help = 'populates the database with initial station data'

    def handle_noargs(self, **options):

        # speedup: manual database commits in bulks
        transaction.set_autocommit(False)

        # cleanup
        Station.objects.all().delete()

        # COUNTRY CODES

        country_codes = {}

        with open(get_file(INPUT_FILES['country_codes']['path'])) as in_file:
            for line in in_file:
                code = get_int(
                    line,
                    INPUT_FILES['country_codes']['characters']['code']
                )
                country = get_string(
                    line,
                    INPUT_FILES['country_codes']['characters']['country']
                ).title()
                country_codes[code] = country


        # preparation for time management
        station_ctr =       0
        start_time =        time.time()
        intermediate_time = start_time
        total_time =        start_time


        # read all weather stations

        for key in INPUT_FILES:

            # ignore country codes
            if key == 'country_codes':
                continue

            # for temperature and precipitation,
            # read the stations and write them into the database

            # for each weather station in file
            with open(get_file(INPUT_FILES[key]['stations']['path'])) as in_file:
                for line in in_file:
                    id = get_int(
                        line,
                        INPUT_FILES[key]['stations']['characters']['station_id']
                    )
                    lat = get_float(
                        line,
                        INPUT_FILES[key]['stations']['characters']['lat'],
                        2
                    )
                    lng = get_float(
                        line,
                        INPUT_FILES[key]['stations']['characters']['lng'],
                        2
                    )
                    elev = get_int(
                        line,
                        INPUT_FILES[key]['stations']['characters']['elv'],
                    )
                    name = get_station_name(
                        line,
                        INPUT_FILES[key]['stations']['characters']['name']
                    )

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
