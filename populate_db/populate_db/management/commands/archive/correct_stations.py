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

    def handle(self, *args, **options):

        # speedup: manual database commits in bulks
        transaction.set_autocommit(False)

        # preparation for time management
        station_ctr =       0
        start_time =        time.time()
        intermediate_time = start_time
        total_time =        start_time


        # read all weather stations and write them into the database

        stations = DATASETS['precipitation']['stations']

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


                # data value check: elevation given?
                for null_value in stations['null_values']:
                    if str(elev) == null_value:
                        elev = None

                # get existing station from database
                existing_station = Station.objects.get(id=id)

                existing_station.lat = lat
                existing_station.lng = lng
                existing_station.elev = elev

                existing_station.save()

                station_ctr += 1
                if station_ctr % BULK_SIZE == 0:
                    transaction.commit()
                    print_time_statistics\
                    (
                        'stations',
                        station_ctr,
                        start_time,
                        intermediate_time
                    )
                    intermediate_time = time.time()

        transaction.commit()
        print ('\nFINISHED WRITING STATIONS TO DATABASE')
        print_time_statistics \
        (
            'stations',
            station_ctr,
            start_time
        )
        print ('')


        # cleanup: manual database commits in bulks
        transaction.set_autocommit(True)
