from pprint import pprint
from typing import Dict, Tuple

from util import force_non_negative, map_value, request_weather_data

# from wikipedia: 'Liste der größten deutschen Onshore-Windparks'
# key: (lat, lon), value: power in MW
ONSHORE_WINDPARK_DICT: Dict[Tuple[float, float], float] = {
    (48.4424, 9.5323): 52.25,
    (48.5851, 11.069): 52.8,
    (49.1746, 9.2456): 54.9,
    (49.4121, 8.0625): 61,
    (49.4316, 7.4319): 52.2,
    (49.4551, 8.0335): 48.8,
    (49.4848, 8.014): 43.2,
    (49.4948, 8.0819): 55,
    (49.5753, 7.399): 70.5,
    (50.0012, 7.2312): 59.8,
    (50.311, 6.2225): 49.65,
    (50.3611, 9.1438): 49.8,
    (50.3725, 9.0912): 41.8,
    (51.0154, 10.3747): 152.25,
    (51.0226, 11.3713): 59.1,
    (51.0228, 6.3148): 67.2,
    (51.0422, 11.4722): 58,
    (51.0754, 11.5751): 188.1,
    (51.1023, 11.212): 82.65,
    (51.1451, 10.172): 58.1,
    (51.2344, 11.4233): 122.1,
    (51.2447, 11.3514): 41.6,
    (51.2522, 11.504): 42.4,
    (51.2643, 8.4149): 65.95,
    (51.2827, 13.1459): 82.8,
    (51.3247, 13.527): 93.1,
    (51.3447, 11.4231): 89.3,
    (51.372, 8.4812): 75.05,
    (51.3825, 8.5444): 129.445,
    (51.3833, 11.393): 72,
    (51.4228, 12.1421): 62.7,
    (51.4316, 11.3839): 83.35,
    (51.4628, 12.423): 77.1,
    (51.4755, 11.2931): 83.05,
    (51.5018, 12.5231): 46,
    (51.5646, 14.2746): 64,
    (51.5739, 11.3623): 114.45,
    (51.5833, 11.277): 79.1,
    (51.5923, 10.5): 92.4,
    (52.005, 12.4951): 128.2,
    (52.0056, 13.1136): 98.8,
    (52.008, 12.0723): 44.9,
    (52.014, 11.224): 76.9,
    (52.0336, 14.2255): 43.2,
    (52.0724, 11.936): 87.65,
    (52.1035, 11.18): 64.1,
    (52.1042, 11.531): 44.4,
    (52.1133, 11.225): 71.3,
    (52.3057, 11.4651): 151.3,
    (52.3223, 12.5218): 175.2,
    (52.355, 12.16): 40.4,
    (52.3946, 11.4233): 93.5,
    (52.523, 7.082): 70.1,
    (52.5241, 10.0234): 40.9,
    (52.54, 12.233): 40.5,
    (52.5836, 7.2457): 41,
    (53.0415, 7.4421): 86.5,
    (53.1915, 12.0137): 75.2,
    (53.2015, 7.0545): 106.25,
    (53.2018, 13.4552): 242.5,
    (53.2147, 7.4218): 77.4,
    (53.2224, 9.2949): 52.9,
    (53.2317, 7.224): 102.34,
    (53.2348, 14.109): 47.1,
    (53.322, 8.571): 49.45,
    (53.3625, 8.4735): 43.6,
    (53.3637, 7.2545): 318.2,
    (53.413, 8.3846): 46.3,
    (53.4255, 13.1911): 202.85,
    (53.494, 8.0444): 65.6,
    (53.5826, 8.56): 302.45,
    (54.29, 11.0636): 57.5,
    (54.364, 8.5413): 293.4,
    (54.3855, 9.1035): 42
}


OFFSHORE_WINDPARK_DICT = {
    (53.4124, 6.2848): 113.4,
    (53.5, 8.1): 110.7,
    (53.5721, 6.2945): 464.8,
    (53.58, 6.33): 312,
    (53.58, 6.48): 332.1,
    (54.003, 6.3554): 60.48,
    (54.1818, 5.4756): 260.4,
    (54.1901, 5.5215): 402,
    (54.2, 6.33): 396,
    (54.213, 5.583): 400,
    (54.23, 7.41): 288,
    (54.246, 6.2725): 200,
    (54.26, 6.19): 497,
    (54.26, 7.41): 295.2,
    (54.3, 6.213): 400,
    (54.3, 6.24): 112,
    (54.3, 6.2758): 203.2,
    (54.3, 7.01): 264,
    (54.3, 7.48): 302.4,
    (54.3632, 12.3904): 48.3,
    (54.4, 7.02): 346,
    (54.4655, 14.0716): 384,
    (54.5002, 14.0405): 353.5,
    (54.54, 7.45): 288,
    (54.5855, 13.0943): 288,
    (55.11, 6.51): 288,
    (55.9, 7.103): 302.4
}

def request_wind_speeds(location_dict):
    """requests the windspeeds specified in the location dict.
    The key of the provided dict has to be in the format (lat, lon).
    Returns dict with key (lat, lon) and value wind_speed"""
    wind_speed = {}
    for lat, lon in location_dict:
        weather = request_weather_data(lat, lon)
        wind_speed[(lat, lon)] = weather['wind']['speed']

    return wind_speed

def calculate_average_weighted_wind_speed(location_weight_dict):
    """Calculates the average wind speed at the (lat, lon) provided by the keys of location_weight_dict.
    The value at each (lat, lon) key is used to weight the wind speed.
    The average weighted wind speed con be used to calculate powers on a grid."""
    weighted_wind_speeds = {}
    wind_speeds = request_wind_speeds(location_weight_dict)

    sum = 0
    for location in location_weight_dict:
        sum += location_weight_dict[location]
    average_power = sum / len(location_weight_dict)

    for location in wind_speeds:
        weighted_wind_speeds[location] = wind_speeds[location] * location_weight_dict[location] / average_power

    sum = 0
    for location in weighted_wind_speeds:
        sum += weighted_wind_speeds[location]

    average_weighted_wind_speed = sum / len(weighted_wind_speeds)

    return average_weighted_wind_speed

def estimate_onshore_wind_power_precise():
    """Estimates the onshore wind power using weather information of 74 locations all over germany and the capacity of windparks located there.
    This location data is provided in the ONSHORE_WINDPARK_DICT.
    Be carefull with this function! Calling it results in 74 API calls.
    See https://docs.google.com/spreadsheets/d/1a9QbTW_9zzluov_hqcWPwHgRYNH03s1lz4pOXHQ5cew/edit?usp=sharing for data."""
    average_weighted_wind_speed = calculate_average_weighted_wind_speed(ONSHORE_WINDPARK_DICT)
    return force_non_negative(map_value(average_weighted_wind_speed, 3, 10, 7.3, 35))

def estimate_offshore_wind_power_precise():
    """Estimates the offshore wind power using weather information of 27 locations in the north- and baltic sea and the capacity of windparks located there.
    This location data is provided in the OFFSHORE_WINDPARK_DICT.
    Be carefull with this function! Calling it results in 27 API calls.
    See https://docs.google.com/spreadsheets/d/1a9QbTW_9zzluov_hqcWPwHgRYNH03s1lz4pOXHQ5cew/edit?usp=sharing for data."""
    average_weighted_wind_speed = calculate_average_weighted_wind_speed(OFFSHORE_WINDPARK_DICT)
    return force_non_negative(map_value(average_weighted_wind_speed, 1.92, 5.71, 2.65, 4.05))

if __name__ == "__main__":
    print(estimate_offshore_wind_power_precise())
    pass