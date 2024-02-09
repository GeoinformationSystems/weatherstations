################################################################################
# INCLUDES
################################################################################

# general python modules
import os
import pandas as pd
import psycopg2
import numpy as np

# django modules
from django.core.management.base import BaseCommand
from django.conf import settings

# own modules
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

        # preparation for time measurement
        record_ctr = 0
        start_time = time.time()
        intermediate_time = start_time

        # connection to postgres database
        conn = psycopg2.connect(database=settings.DATABASES['default']['NAME'],
                        host=settings.DATABASES['default']['HOST'],
                        user=settings.DATABASES['default']['USER'],
                        password=settings.DATABASES['default']['PASSWORD'],
                        port=settings.DATABASES['default']['PORT']) 
        cursor = conn.cursor()

        # create table if not exist
        cursor.execute("CREATE TABLE IF NOT EXISTS public.betav4(stationidyear character varying(15) NOT NULL,jan numeric(5),feb numeric(5),mar numeric(5),apr numeric(5),may numeric(5),jun numeric(5),jul numeric(5),aug numeric(5),sep numeric(5),oct numeric(5),nov numeric(5),dec numeric(5))")
        conn.commit()

        cursor.execute("DELETE FROM betav4")

        csvsFolder = os.path.join(os.getcwd(), DATASETS['precipitation']['dataRaw']['folder'] + testfolder)
        nullValue = DATASETS['precipitation']['data']['null_values'][0]

        for filename in os.listdir(csvsFolder):
            if os.path.isfile(os.path.join(csvsFolder, filename)):
                with open(os.path.join(csvsFolder, filename), 'r') as f:
                    # initial fill data variable when reading a new file with missing data values
                    currentMonths = {
                        1: nullValue, 2: nullValue, 3: nullValue, 4: nullValue, 5: nullValue, 6: nullValue, 7: nullValue, 8: nullValue, 9: nullValue, 10: nullValue, 11: nullValue, 12: nullValue
                    }
                    currentyear = nullValue

                    # read line and get value
                    for line in f:
                        station_id = get_string(
                            line,
                            DATASETS['precipitation']['dataRaw']['characters']['station_id']
                        )
                        year = get_int(
                            line,
                            DATASETS['precipitation']['dataRaw']['characters']['year']
                        )
                        month = get_int(
                            line,
                            DATASETS['precipitation']['dataRaw']['characters']['month']
                        )
                        value = get_int(
                            line,
                            DATASETS['precipitation']['dataRaw']['characters']['value']
                        )

                        # if year has not changed according to former line just store the value for the month
                        if year == currentyear:
                            currentMonths[month] = value
                        else:
                            # store the data to the database when a year has changed, but not at the beginning of reading that file=> nullValue
                            if currentyear != nullValue:
                                cursor.execute("INSERT INTO betav4 (stationidyear, jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (station_id+str(currentyear), currentMonths[1], currentMonths[2], currentMonths[3], currentMonths[4], currentMonths[5], currentMonths[6], currentMonths[7], currentMonths[8], currentMonths[9], currentMonths[10], currentMonths[11], currentMonths[12]))

                            # set this lines year as new working year  after last years data was stored in database
                            currentyear = year

                            # reset months data values after the last year was stored in database
                            for i in currentMonths:
                                currentMonths[i] = nullValue

                            # and set the month value of the current line
                            currentMonths[month] = value
                    
                    record_ctr += 1
                    if record_ctr % BULK_SIZE == 0:
                        print_time_statistics('PROCESSED FILES: ', '', record_ctr, start_time, intermediate_time)
                        intermediate_time = time.time()
                # END of "with open": finished read line by line

                # IF end of file was reached store the last year data (no "change of year" happens at the end of the file)
                if currentyear != nullValue:
                    cursor.execute("INSERT INTO betav4 (stationidyear, jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (station_id+str(currentyear), currentMonths[1], currentMonths[2], currentMonths[3], currentMonths[4], currentMonths[5], currentMonths[6], currentMonths[7], currentMonths[8], currentMonths[9], currentMonths[10], currentMonths[11], currentMonths[12]))
                    conn.commit()

        print_time_statistics('FINISHED WRITING TO DATABASE Total files:', '', record_ctr, start_time, intermediate_time)
        intermediate_time = time.time()
        
        view_with_eq_width = '''create or replace view export(stationidyear, jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec) as
            SELECT
                cast(stationidyear as char(15)) AS stationidyear,
                cast(jan as char(5)) AS jan,
                cast(feb as char(5)) AS feb,
                cast(mar as char(5)) AS mar,
                cast(apr as char(5)) AS apr,
                cast(may as char(5)) AS may,
                cast(jun as char(5)) AS jun,
                cast(jul as char(5)) AS jul,
                cast(aug as char(5)) AS aug,
                cast(sep as char(5)) AS sep,
                cast(oct as char(5)) AS oct,
                cast(nov as char(5)) AS nov,
                cast(dec as char(5)) AS dec
            FROM betav4;'''
        cursor.execute(view_with_eq_width)
        conn.commit()

        sql = "COPY (SELECT * FROM export) TO STDOUT WITH CSV DELIMITER ','"
        with open(os.path.join(os.getcwd(), DATASETS['precipitation']['data']['path']), "w") as file:
            cursor.copy_expert(sql, file)

        print_time_statistics('FINISHED WRITING DATA TO FILE', '', 0, start_time, intermediate_time)
        intermediate_time = time.time()

        conn.close()

