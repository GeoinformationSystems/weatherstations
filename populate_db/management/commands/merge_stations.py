################################################################################
# MERGE STATION DUPLICATES
################################################################################

# execute me using:
# python manage.py merge_stations


################################################################################
# CONSTANTS
################################################################################

# check only limited set of data
TEST_RUN = False

# maximum distance between two stations with the same id
# to say that they are "the same" / have only slightly moved
DISTANCE_THRESHOLD = 2.0 # [km]

################################################################################
# INCLUDES
################################################################################

# general python modules
import os
import time
from haversine import haversine

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
    help = "Identify duplicates among the stations based on their id and their \
            geographic location and merge them"


    # ==========================================================================
    # MERGE TWO STATION DATA
    # ==========================================================================

    def merge_stations(self, A, B):
        print A.name, B.name

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

        # get all countries which have stations
        ## use a set to avoid duplicates
        countries = set()
        for station in Station.objects.all():
            countries.add(station.country)

        distances = [0]*500

        # find duplicates among stations in one country
        for country in countries:

            # test run
            if (TEST_RUN) and (country != 'Algeria'): continue

            ## get all stations in this country
            stations_in_country = Station.objects.filter(country=country)

            ## find duplicates
            i = 0
            j = 1
            end = len(stations_in_country)-1


            while i < end:
                j = i+1
                while j < end:

                    ## get stations
                    A = stations_in_country[i]
                    B = stations_in_country[j]

                    ## check if first 8 digits of id are the same
                    ## -> because last three digits might be increments of
                    ##    the same station that has moved or so...
                    if (str(A.id)[0:7] == str(B.id)[0:7]):

                        ## check if the distance between both stations is small
                        ## -> because it could be the station has slightly moved
                        A_coords = (A.lat, A.lng)
                        B_coords = (B.lat, B.lng)
                        dist = haversine(A_coords, B_coords)

                        dist_idx = int(round(dist*10))
                        if dist_idx < 500:
                            distances[dist_idx] += 1

                        if (d < DISTANCE_THRESHOLD):

                            ## merge station data
                            self.merge_stations(A, B)

                    ## check next station
                    j += 1
                i += 1

        print distances



        # finalize
        transaction.commit()
        print 'FINISHED UPDATING DATABASE'
        print_time_statistics('updated', 'stations', station_ctr, start_time)
        print ''

        # cleanup: manual database commits in bulks
        transaction.set_autocommit(True)
