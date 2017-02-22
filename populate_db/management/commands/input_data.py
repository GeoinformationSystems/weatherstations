################################################################################
# GLOBAL CONSTANTS
################################################################################

# extend of geographic coordinate system
MAX_LAT = 90
MAX_LNG = 180

# number of months in a year
NUM_MONTHS = 12

# name of months
MONTHS = \
[
    ['m01', 'Jan'], ['m02', 'Feb'], ['m03', 'Mar'],
    ['m04', 'Apr'], ['m05', 'May'], ['m06', 'Jun'],
    ['m07', 'Jul'], ['m08', 'Aug'], ['m09', 'Sep'],
    ['m10', 'Oct'], ['m11', 'Nov'], ['m12', 'Dec']
]

# max. possible number of gaps (consecutive months with missing data) to count
MAX_GAP = 10000

# size of consecutive database queries that are executed at once
# optimal: [1000 .. 5000]
BULK_SIZE = 1000

################################################################################
# INPUT DATA FROM project/data FOLDER
# DATA FILES AND CHARACTER MAPPINGS
################################################################################

COUNTRY_CODES = \
{
    'path':       'data/meta/country_codes',
    'characters':
    {
        'code':             [0,2],
        'country':          [4,60],
    },
}

DATASETS = \
{
    'temperature' :
    {
        'stations':
        {
            'path': 'data/GHCN_monthly_v3_temperature/ghcnm.tavg.v3.3.0.20170203.qca.inv',
            'null_values':      ['-999'],
            'characters':
            {
                'station_id':   [0,10],
                'lat':          [12,19],
                'lng':          [21,29],
                'elv':          [31,37],
                'name':         [38,68],    # N.B. a country name can be inside
            },
        },
        'data':
        {
            'path': 'data/GHCN_monthly_v3_temperature/ghcnm.tavg.v3.3.0.20170203.qca.dat',
            'division_factor':  100,
            'null_values':      ['-9999','-8888'],
            'characters':
            {
                'station_id':   [0,10],
                'year':         [11,14],
                'value':        [15,18],    # should always be 'TAVG'
                '1':            [19,23],    # Jan
                '2':            [27,31],    # Feb
                '3':            [35,39],    # ...
                '4':            [43,47],
                '5':            [51,55],
                '6':            [59,63],
                '7':            [67,71],
                '8':            [75,79],
                '9':            [83,87],
                '10':           [91,95],
                '11':           [99,103],
                '12':           [107,111],  # Dec
            },
        },
    },
    'precipitation' :
    {
        'stations':
        {
            'path': 'data/GHCN_monthly_v2_precipitation/v2.prcp.inv',
            'null_values':      ['-999'],
            'characters':
            {
                'station_id':   [0,10],
                'lat':          [44,48],
                'lng':          [50,57],
                'elv':          [58,61],
                'name':         [12,42],    # N.B. a country name can be inside
            },
        },
        'data':
        {
            'path': 'data/GHCN_monthly_v2_precipitation/v2.prcp',
            'division_factor':  10,
            'null_values':      ['-9999','-8888'],
            'characters':
            {
                'station_id':   [0,10],
                'year':         [12,15],
                'has_duplicates': [11,11],
                '1':            [16,20],    # Jan
                '2':            [21,25],    # Feb
                '3':            [26,30],    # ...
                '4':            [31,35],
                '5':            [36,40],
                '6':            [41,45],
                '7':            [46,50],
                '8':            [51,55],
                '9':            [56,60],
                '10':           [61,65],
                '11':           [66,70],
                '12':           [71,75],    # Dec
            },
        },
    },
}
