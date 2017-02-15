################################################################################
# INPUT DATA FROM project/data FOLDER
# DATA FILES AND CHARACTER MAPPINGS
################################################################################

INPUT_FILES = \
{
    'country_codes':
    {
        'path':       'data/meta/country_codes',
        'characters':
        {
            'code':             [0,2],
            'country':          [4,60],
        },
    },
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
                'm01':          [19,23],
                'm02':          [27,31],
                'm03':          [35,39],
                'm04':          [43,47],
                'm05':          [51,55],
                'm06':          [59,63],
                'm07':          [67,71],
                'm08':          [75,79],
                'm09':          [83,87],
                'm10':          [91,95],
                'm11':          [99,103],
                'm12':          [107,111],
            },
        },
        'argument_alternatives':
        [
            'T', 't',
            'Tmp', 'tmp',
            'Temp', 'temp',
            'Temperature', 'temperature'
        ],
        'model_name':   'TemperatureData',
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
                'm01':          [16,20],
                'm02':          [21,25],
                'm03':          [26,30],
                'm04':          [31,35],
                'm05':          [36,40],
                'm06':          [41,45],
                'm07':          [46,50],
                'm08':          [51,55],
                'm09':          [56,60],
                'm10':          [61,65],
                'm11':          [66,70],
                'm12':          [71,75],
            },
        },
        'argument_alternatives':
        [
            'P', 'p',
            'Prec', 'prec',
            'Prcp', 'prcp',
            'Precipitation', 'precipitation'
        ],
        'model_name':   'PrecipitationData',
    },
}
