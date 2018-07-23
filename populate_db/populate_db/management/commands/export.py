################################################################################
# INCLUDES
################################################################################

# general python modules
import csv

# django modules
from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str

# own modules
from populate_db.models import *
from populate_db.management.commands.input_data import *

################################################################################
# EXPORT THE CLIMATE DATABASE (STATIONS) TO SHOW IT IN QGIS
################################################################################

# execute me using:
# python manage.py export


################################################################################
# GLOBAL CONSTANTS
################################################################################

# export file name
EXPORT_FILE = "data/qgis/stations.csv"


################################################################################
# MAIN
################################################################################

class Command(BaseCommand):
    help = "Exports all promising Stations to a csv file: \
            - name, country \
            - lat, lng \
            - complete_data_rate, largest_gap"

    # ==========================================================================
    # MAIN
    # ==========================================================================

    def handle(self, *args, **options):
        # get all promising stations
        promising_stations = Station.objects \
            .filter(complete_data_rate__gte=MIN_COVERAGE) \
            .filter(largest_gap__lte=MAX_GAPS)

        # export to csv
        with open(EXPORT_FILE, 'wb') as export_file:
            writer = csv.writer(
                export_file,
                delimiter=',',
                quotechar='"'
            )

            writer.writerow([
                smart_str(u"name"),
                smart_str(u"country"),
                smart_str(u"lat"),
                smart_str(u"lng"),
                smart_str(u"coverage_rate"),
                smart_str(u"largest_gap"),
            ])

            for station in promising_stations:
                writer.writerow([
                    smart_str(station.name),
                    smart_str(station.country),
                    smart_str(station.lat),
                    smart_str(station.lng),
                    smart_str(station.complete_data_rate),
                    smart_str(station.largest_gap),
                ])
