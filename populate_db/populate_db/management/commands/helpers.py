################################################################################
# INCLUDES
################################################################################

# general python modules
import os
import time
import math


################################################################################
# HELPER FUNCTIONS
################################################################################

# ------------------------------------------------------------------------------
def get_file(file_id):
    return os.path.abspath(os.path.join(file_id))


# ------------------------------------------------------------------------------
def get_string(in_string, indices):
    return in_string[indices[0]:indices[1] + 1].strip()


# ------------------------------------------------------------------------------
def get_int(in_string, indices):
    return int(float(in_string[indices[0]:indices[1] + 1]))


# ------------------------------------------------------------------------------
def get_float(in_string, indices, decimals=2):
    full_float = float(in_string[indices[0]:indices[1] + 1])
    decimal_format = '%.' + str(decimals) + 'f'
    return float(decimal_format % full_float)


# ------------------------------------------------------------------------------
def get_station_name(in_string, indices):
    """
    goal: we want the name of a weather station, without the country name
        -> 'PUENTARES' or 'GRAVENHURST' or 'SAN JOSE/CENTRAL OFFICE'
    problem: in the data file there are two columns: station and country name,
        in most cases there is only a station name
        -> 'PUNTARENAS                     '
        in some cases there is also a country name
        -> 'GRAVENHURST         CANADA     '
        and few cases the name is very long and reaches into country name column
        -> 'SAN JOSE/CENTRAL OFFICE        '
    => we need to distinguish them and parse only the station name
    idea: read the whole string and test from the beginning if there is anything
        that delimits the station name string, e.g. '  ' or '(' without a ')'
        If so, assume the station name stops there and strip the rest
        -> works well, except if the station name reaches until one character
        before the country name - but this case can not be distinguished
    """
    str_name_full = in_string[indices[0]:indices[1] + 1].strip()

    deliminator_idxs = [len(str_name_full)]  # default deliminator: end of string

    # find double whitespace '  '
    if str_name_full.find('  ') > -1:
        deliminator_idxs.append(str_name_full.find('  '))

    # find lonely opening parenthesis '('
    if (str_name_full.find('(') > -1) and (str_name_full.find(')') == -1):
        deliminator_idxs.append(str_name_full.find('('))

    # get the index of the first occurence of a deliminator
    deliminator_idxs.sort()

    return str_name_full[0:deliminator_idxs[0]].strip().title()


# ------------------------------------------------------------------------------
def print_time_statistics(
        operation_name='saved',
        records_name='records',
        record_ctr=0,
        start_time=0,
        intermediate_time=0
):
    new_time = time.time()

    print_str = str(
        operation_name
        + str(record_ctr).rjust(8)
        + ' '
        + str(records_name)
    )

    if intermediate_time > 0:
        print_str += str(' | '
                         + str('%.2f' % (new_time - intermediate_time)).rjust(5)
                         + ' s'
                         )
    else:
        print_str += str(' | '
                         + ''.rjust(5)
                         + '  '
                         )

    total_time_s = new_time - start_time
    total_h = int(math.floor(total_time_s / (60 * 60)))
    leftover_time_s = total_time_s - math.floor(total_h * 60 * 60)
    total_m = int(math.floor(leftover_time_s / 60))
    total_s = leftover_time_s - math.floor(total_m * 60)

    # prevent division by 0 error:
    if record_ctr == 0:
        time_per_thousand = 0
    else:
        time_per_thousand = 1000 * (new_time - start_time) / record_ctr

    print_str += str(' | total: '
                     + str(total_h).zfill(2).rjust(2)
                     + ':'
                     + str(total_m).zfill(2).rjust(2)
                     + ':'
                     + str('%05.2f' % total_s).rjust(5)
                     + ' | time / 1000 '
                     + ': '
                     + str('%.2f' % time_per_thousand).rjust(5)
                     + ' s'
                     )

    print print_str
