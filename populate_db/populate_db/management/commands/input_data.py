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
BULK_SIZE = 1000

# Only include stations with the following characteristics:
MIN_COVERAGE = 0.75  # at least x % coverage
MAX_GAPS = 120  # maximum number of consecutive missing months

################################################################################
# INPUT DATA FROM project/data FOLDER
# DATA FILES AND CHARACTER MAPPINGS
################################################################################

COUNTRY_CODES = {
    'path': 'data/meta/v2.country.codes',
    'characters':
        {
            'code': [0, 2],
            'country': [4, 60],
        },
}

DATASETS = {
    'precipitation':
        {
            'stations':
                {
                    'path': 'data/GHCN_monthly_v2_precipitation/v2.prcp.inv',
                    'null_values': ['-999'],
                    'characters':
                        {
                            'station_id': [0, 10],
                            'lat': [43, 48],
                            'lng': [50, 56],
                            'elv': [57, 61],
                            'name': [12, 42],  # N.B. a country name can be inside
                        },
                    'pandas_characters':
                        {
                            'station_id': [0, 11]
                        }
                },
            'data':
                {
                    'path': 'data/GHCN_monthly_v2_precipitation/v2.prcp',
                    'division_factor': 10,
                    'null_values': ['-9999', '-8888'],
                    'characters':
                        {
                            'station_id': [0, 10],
                            'year': [12, 15],
                            'has_duplicates': [11, 11],
                            '1': [16, 20],  # Jan
                            '2': [21, 25],  # Feb
                            '3': [26, 30],  # ...
                            '4': [31, 35],
                            '5': [36, 40],
                            '6': [41, 45],
                            '7': [46, 50],
                            '8': [51, 55],
                            '9': [56, 60],
                            '10': [61, 65],
                            '11': [66, 70],
                            '12': [71, 75],  # Dec
                        },
                    'pandas_characters':
                        {
                            'station_id': [0, 11],
                            'year': [12, 16],
                            '1': [16, 21],  # Jan
                            '2': [21, 26],  # Feb
                            '3': [26, 31],  # ...
                            '4': [31, 36],
                            '5': [36, 41],
                            '6': [41, 46],
                            '7': [46, 51],
                            '8': [51, 56],
                            '9': [56, 61],
                            '10': [61, 66],
                            '11': [66, 71],
                            '12': [71, 76],  # Dec
                        },
                },
        },
    'temperature':
        {
            'stations':
                {
                    'path': 'data/GHCN_monthly_v3_temperature/ghcnm.tavg.v3.3.0.latest.qca.inv',
                    'null_values': ['-999'],
                    'characters':
                        {
                            'station_id': [0, 10],
                            'lat': [12, 19],
                            'lng': [21, 29],
                            'elv': [31, 37],
                            'name': [38, 68],  # N.B. a country name can be inside
                        },
                    'pandas_characters':
                        {
                            'station_id': [0, 11]
                        }
                },
            'data':
                {
                    'path': 'data/GHCN_monthly_v3_temperature/ghcnm.tavg.v3.3.0.latest.qca.dat',
                    'division_factor': 100,
                    'null_values': ['-9999', '-8888'],
                    'characters':
                        {
                            'station_id': [0, 10],
                            'year': [11, 14],
                            'value': [15, 18],  # should always be 'TAVG'
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
