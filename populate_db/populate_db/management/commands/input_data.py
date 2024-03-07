################################################################################
# GLOBAL CONSTANTS
################################################################################

# extend of geographic coordinate system
MAX_LAT = 90
MAX_LNG = 180

# number of months in a year
NUM_MONTHS = 12

# name of months
MONTHS = [
    ['m01', 'Jan'], ['m02', 'Feb'], ['m03', 'Mar'],
    ['m04', 'Apr'], ['m05', 'May'], ['m06', 'Jun'],
    ['m07', 'Jul'], ['m08', 'Aug'], ['m09', 'Sep'],
    ['m10', 'Oct'], ['m11', 'Nov'], ['m12', 'Dec']
]

# max. possible number of gaps (consecutive months with missing data) to count
MAX_GAP = 10000

# size of consecutive database queries that are executed at once
# optimal: [1000 .. 5000]
BULK_SIZE = 5000

# Only include stations with the following characteristics:
MIN_COVERAGE = 0.75  # at least x % coverage
MAX_GAPS = 120  # maximum number of consecutive missing months

################################################################################
# INPUT DATA FROM project/data FOLDER
# DATA FILES AND CHARACTER MAPPINGS
################################################################################

COUNTRY_CODES = {
    'path': 'data/meta/ghcnm-countries.txt',
    'characters':
        {
            'code': [0, 2],
            'country': [3, 65],
        },
}

DATASETS = {
    'precipitation':
        {
            'stations':
                {
                    'path': 'data/GHCN_monthly_prec/ghcn-m_v4_prcp_inventory.txt',
                    'null_values': ['-999'],
                    'characters':
                        {
                            'station_id': [0, 10],
                            'country_code' : [0, 1],
                            'lat': [12, 19],
                            'lng': [21, 29],
                            'elv': [31, 36],
                            'name': [41, 78],  # N.B. a country name can be inside
                        },
                    'pandas_characters':
                        {
                            'station_id': [0, 11]
                        }
                },
            'data':
                {
                    'path': 'data/GHCN_monthly_prec/precv4_full.csv',
                    'division_factor': 10,
                    'null_values': ['-9999','-1','-300'],
                    'characters':
                        {
                            'station_id': [0, 10],
                            'year': [11, 14],
                            '1': [16, 20],  # Jan
                            '2': [22, 26],  # Feb
                            '3': [28, 32],  # ...
                            '4': [34, 38],
                            '5': [40, 44],
                            '6': [46, 50],
                            '7': [52, 56],
                            '8': [58, 62],
                            '9': [64, 68],
                            '10': [70, 74],
                            '11': [76, 80],
                            '12': [82, 86],  # Dec
                        },
                    'pandas_characters':
                        {
                            'station_id': [0, 11],
                            'year': [11, 15],
                            '1': [16, 21],  # Jan
                            '2': [22, 27],  # Feb
                            '3': [28, 33],  # ...
                            '4': [34, 39],
                            '5': [40, 45],
                            '6': [46, 51],
                            '7': [52, 57],
                            '8': [58, 63],
                            '9': [64, 69],
                            '10': [70, 75],
                            '11': [76, 81],
                            '12': [82, 87],  # Dec
                        },
                },
            'dataRaw':
                {
                    'folder': 'data/GHCN_monthly_prec/v4_raw',
                    'characters':
                        {
                            'station_id': [0, 10],
                            'year': [83, 86],
                            'month': [87, 88],
                            'value': [90, 95]
                        },
                },
        },
    'temperature':
        {
            'stations':
                {
                    'path': 'data/GHCN_monthly_temp/ghcnm.tavg.v4.0.1.latest.qcf.inv',
                    'null_values': ['-999'],
                    'characters':
                        {
                            'station_id': [0, 10],
                            'country_code': [0, 1],
                            'lat': [12, 19],
                            'lng': [21, 29],
                            'elv': [31, 36],
                            'name': [38, 68],  # N.B. a country name can be inside
                        },
                    'pandas_characters':
                        {
                            'station_id': [0, 11]
                        }
                },
            'data':
                {
                    'path': 'data/GHCN_monthly_temp/ghcnm.tavg.v4.0.1.latest.qcf.dat',
                    'division_factor': 100,
                    'null_values': ['-9999', '-8888'],
                    'characters':
                        {
                            'station_id': [0, 10],
                            'year': [11, 14],
                            '1': [19, 23],  # Jan
                            '2': [27, 31],  # Feb
                            '3': [35, 39],  # ...
                            '4': [43, 47],
                            '5': [51, 55],
                            '6': [59, 63],
                            '7': [67, 71],
                            '8': [75, 79],
                            '9': [83, 87],
                            '10': [91, 95],
                            '11': [99, 103],
                            '12': [107, 111],  # Dec
                        },
                    'pandas_characters':
                        {
                            'station_id': [0, 11],
                            'year': [11, 15],
                            '1': [19, 24],  # Jan
                            '2': [27, 32],  # Feb
                            '3': [35, 40],  # ...
                            '4': [43, 48],
                            '5': [51, 56],
                            '6': [59, 64],
                            '7': [67, 72],
                            '8': [75, 80],
                            '9': [83, 88],
                            '10': [91, 96],
                            '11': [99, 104],
                            '12': [107, 112],  # Dec
                        },
                },
        },
}
