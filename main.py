#!/usr/bin/python

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CREATE AND POPULATE THE CLIMATE DATA BASE WITH
# STATIONS AND THEIR HISTORICAL TEMPERATURE AND PRECIPITATION DATA
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import psycopg2     # for using postgresql database


################################################################################
# GLOBAL CONSTANTS
################################################################################

INPUT_FILES = \
{
    'country_codes':    'meta/country_codes',
    'temperature' :
    {
        'stations':     'GHCN_monthly_v3_temperature/ghcnm.tavg.v3.3.0.20170203.qca.inv',
        'data':         'GHCN_monthly_v3_temperature/ghcnm.tavg.v3.3.0.20170203.qca.dat'
    },
    'precipitation' :
    {
        'stations':     'GHCN_monthly_v2_precipitation/v2.prcp.inv',
        'data':         'GHCN_monthly_v2_precipitation/v2.prcp'
    }
}

DATABASE = {
    'name':             'climatecharts_weatherstations',
    'host':             '127.0.0.1',    # localhost
    'un':               'postgres',
    'pw':               'postgres'
}


################################################################################
# MAIN
################################################################################

# connect to database and get a handle on it (cursor)

try:
    db_connection = psycopg2.connect(
        'dbname=' + DATABASE['name'] + ' host=' + DATABASE['host'] +
        ' user=' + DATABASE['un'] + ' password=' + DATABASE['pw']
    )
except:
    print "Can not connect to database"

db_cursor = db_connection.cursor()

# temperature dataset
# ===================

# fill all stations
