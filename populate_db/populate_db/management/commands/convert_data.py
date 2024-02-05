################################################################################
# INCLUDES
################################################################################
import os

import pandas as pd
import psycopg2
# general python modules
from haversine import haversine
from itertools import islice
# import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import io

# django modules
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from django.contrib.gis.geos import Point

# own modules
from populate_db.models import Station, StationData, StationDuplicate
from populate_db.management.commands.input_data import *
from populate_db.management.commands.helpers import *

################################################################################
# CONVERT V4 BETA DATA
################################################################################

# execute me using:
# python manage.py convert_data

################################################################################
# GLOBAL CONSTANTS
################################################################################

TEST_RUN = False


################################################################################
# MAIN
################################################################################

class Command(BaseCommand):
    help = "Converts BetaV4 single CSV files into one single file"

    # ==========================================================================
    # MAIN
    # ==========================================================================

    def handle(self, *args, **options):

        testfolder = ""
        if TEST_RUN:
            testfolder = "0test/"

        conn = psycopg2.connect(database="postgres",
                        host="localhost",
                        user="postgres",
                        password="postgres",
                        port="5432")
        cursor = conn.cursor()

        cursor.execute("DELETE FROM precv4")

        csvsFolder = DATASETS['precipitationV4Raw']['data']['folder'] + testfolder

        for filename in os.listdir(os.getcwd()+csvsFolder):
            if os.path.isfile(os.path.join(os.getcwd()+csvsFolder, filename)):
                with open(os.path.join(os.getcwd()+csvsFolder, filename), 'r') as f:
                    # initial fill data variable when reading a new file with missing data values
                    currentMonths = {
                        1: -9999, 2: -9999, 3: -9999, 4: -9999, 5: -9999, 6: -9999, 7: -9999, 8: -9999, 9: -9999, 10:-9999, 11: -9999, 12:-9999
                    }
                    currentyear = -9999

                    # read line and get value
                    for line in f:
                        station_id = get_string(
                            line,
                            DATASETS['precipitationV4Raw']['data']['characters']['station_id']
                        )
                        year = get_int(
                            line,
                            DATASETS['precipitationV4Raw']['data']['characters']['year']
                        )
                        month = get_int(
                            line,
                            DATASETS['precipitationV4Raw']['data']['characters']['month']
                        )
                        value = get_int(
                            line,
                            DATASETS['precipitationV4Raw']['data']['characters']['value']
                        )

                        # IF year has not changed according to former line just store the value for the month
                        if year == currentyear:
                            currentMonths[month] = value
                        else:
                            # store the data to the database when a year has changed, but not at the beginning of reading that file=> -9999
                            if currentyear != -9999:
                                cursor.execute("INSERT INTO precv4 (stationidyear, jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (station_id+str(currentyear), currentMonths[1], currentMonths[2], currentMonths[3], currentMonths[4], currentMonths[5], currentMonths[6], currentMonths[7], currentMonths[8], currentMonths[9], currentMonths[10], currentMonths[11], currentMonths[12]))

                            # set this lines year as new working year  after last years data was stored in database
                            currentyear = year

                            # reset months data values after the last year was stored in database
                            for i in currentMonths:
                                currentMonths[i] = -9999

                            # and set the month value of the current line
                            currentMonths[month] = value

                # END of "with open": finished read line by line

                # IF end of file was reached store the last year data (no "change of year" happens at the end of the file)
                if currentyear != -9999:
                    cursor.execute("INSERT INTO precv4 (stationidyear, jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (station_id+str(currentyear), currentMonths[1], currentMonths[2], currentMonths[3], currentMonths[4], currentMonths[5], currentMonths[6], currentMonths[7], currentMonths[8], currentMonths[9], currentMonths[10], currentMonths[11], currentMonths[12]))
                    conn.commit()

        # view_with_eq_width = '''create or replace view view_name(stationidyear, jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec) as
        #     SELECT
        #         cast(stationidyear as char(15)) AS stationidyear,
        #         cast(jan as char(15)) AS jan,
        #         cast(feb as char(15)) AS feb,
        #         cast(mar as char(15)) AS mar,
        #         cast(apr as char(15)) AS apr,
        #         cast(may as char(15)) AS may,
        #         cast(jun as char(15)) AS jun,
        #         cast(jul as char(15)) AS jul,
        #         cast(aug as char(15)) AS aug,
        #         cast(sep as char(15)) AS sep,
        #         cast(oct as char(15)) AS oct,
        #         cast(nov as char(15)) AS nov,
        #         cast(dec as char(15)) AS dec
        #         # jan::character(5)            AS jan,
        #         # feb::character(5)            AS feb,
        #         # mar::character(5)            AS mar,
        #         # apr::character(5)            AS apr,
        #         # may::character(5)            AS may,
        #         # jun::character(5)            AS jun,
        #         # jul::character(5)            AS jul,
        #         # aug::character(5)            AS aug,
        #         # sep::character(5)            AS sep,
        #         # oct::character(5)            AS oct,
        #         # nov::character(5)            AS nov,
        #         # dec::character(5)            AS dec
        #     FROM precv4;'''
        # cursor.execute(view_with_eq_width);
        # conn.commit()
        # conn.close()

