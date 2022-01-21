from typing import Dict
import requests as req
import json
from time import sleep
import datetime
from math import sin, pi, e


import rgb_controller

def map_value(x, a, b, c, d):
    """maps the value x in relation to a and b to c and d"""
    return ((c - d) * (x - a)) / (a - b) + c

def map_value_clamp(x, a, b, c, d):
    """maps the value x in relation to a and b to c and d, then clamps it to that range"""
    v = map_value(x, a, b, c, d)
    if v < c and v < d:
        return min(c, d)
    elif v > c and v > d:
        return max(c, d)
    return v

def force_non_negative(x: float) -> float:
    return x if x > 0 else 0

# coordinates of the city oldenburg
OLDENBURG_LAT   = 53.14118
OLDENBURG_LON   = 8.21467

# coordinates of the offshore wind park BorWinAlpha
BOR_WIN_LAT     = 54.3548547
BOR_WIN_LON     = 6.02508583

# coordinates of the onshore wind park Holtriem
HOLTRIEM_LAT    = 53.610278
HOLTRIEM_LON    = 7.429167

def request_weather_data(lat, lon):
    """Requests weather data using the openweathermap api."""
    with open("KEY.txt") as f:
        key = f.read().rstrip()
    res = req.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}")
    return json.loads(res.text)

def get_wind_speed(weather_data=None, lat=None, lon=None):
    """Returns the wind speed from a specified weather_data dict or if no weather_data is 
    provided, requests the wind speed at the specified lat and lon using the openweather api"""
    weather_data = request_weather_data(lat, lon) if weather_data == None else weather_data
    return weather_data['wind']['speed']

def get_cloudiness(weather_data=None, lat=None, lon=None):
    """Returns the cloudiness from a specified weather_data dict or if no weather_data is 
    provided, requests the cloudiness at the specified lat and lon using the openweather api"""
    weather_data = request_weather_data(lat, lon) if weather_data == None else weather_data
    return weather_data['clouds']['all']

def estimate_needed_power(time: datetime.time, average: float = 60, deviation: float = 20):
    """Estimates the needed power at a given time
    
    args:
        time: datetime.time     time
        average: float          average power needed
        deviation: float        difference between highest and lowest power consumption

    returns: float              estimated power consumption in GW
    """
    return deviation / 2 * sin(2 * pi / 24 * ((time.hour + time.minute / 60) - 6)) + average

def estimate_currently_needed_power():
    return estimate_needed_power(datetime.datetime.now())

def estimate_onshore_wind_power(wind_speed: float) -> float:
    """Uses wind_speed to estimate the onshore wind power production.
    See https://docs.google.com/spreadsheets/d/1a9QbTW_9zzluov_hqcWPwHgRYNH03s1lz4pOXHQ5cew/edit?usp=sharing
    and https://www.desmos.com/calculator/9z13kqfsx0"""
    return force_non_negative(-e**(-0.53*(wind_speed-10))+32)

def estimate_offshore_wind_power(wind_speed):
    """Uses wind_speed to estimate the offshore wind power production.
    See https://docs.google.com/spreadsheets/d/1a9QbTW_9zzluov_hqcWPwHgRYNH03s1lz4pOXHQ5cew/edit?usp=sharing"""
    if wind_speed < 10:
        return force_non_negative(map_value(wind_speed, 4.65, 9.5, 0.732, 5.465))
    else:
        return force_non_negative(map_value(wind_speed, 9.89, 15.16, 5.465, 4.8))

SOLAR_FACTOR = {
    "jan": 1.086,
    "feb": 1.459,
    "mar": 2.032,
    "apr": 2.582,
    "may": 2.677,
    "jun": 2.818,
    "jul": 3.532,
    "aug": 3.145,
    "sep": 2.463,
    "oct": 2.463,
    "nov": 2.463,
    "dec": 1.0
}

SOLAR_CONSTANT = 7

def estimate_solar_power(date: datetime.datetime, cloudiness):
    """estimates the solar power using the daytime and the date"""
    factor = list(SOLAR_FACTOR.values())[date.month - 1]
    cloud_factor = 1 - cloudiness / 100 + 0.6
    cloud_factor = map_value_clamp(cloud_factor, 0, 1, 0, 1)
    return factor * cloud_factor * SOLAR_CONSTANT * force_non_negative(sin(2 * pi / 24 * ((date.hour + date.minute / 60) - 6)))

def estimate_current_solar_power(cloudiness):
    return estimate_solar_power(datetime.datetime.now(), cloudiness)

def estimate_power(holtriem_wind=None, bor_win_wind=None, cloudiness=None, log=True):
    """estimates the current power. if no parameters are provided, it will request 
    everything it needs automatically. However, you can specify the wind speeds and the cloundiness.
    If the parameter log is set to False, it will not print information to stdout"""
    needed_power = estimate_currently_needed_power()

    h_wind = get_wind_speed(lat=HOLTRIEM_LAT, lon=HOLTRIEM_LON) if holtriem_wind == None else holtriem_wind
    onshore = estimate_onshore_wind_power(h_wind)

    b_wind = get_wind_speed(lat=BOR_WIN_LAT, lon=BOR_WIN_LON) if bor_win_wind == None else bor_win_wind
    offshore = estimate_offshore_wind_power(b_wind)

    cloudiness = get_cloudiness(lat=OLDENBURG_LAT, lon=OLDENBURG_LON) if cloudiness == None else cloudiness
    solar = estimate_current_solar_power(cloudiness)

    renewable_power_supply = onshore + offshore + solar

    conv_power = force_non_negative(needed_power - renewable_power_supply)

    if log:
        print(f"[INFO] estimated power consumption: {needed_power} GW")
        print(f"[INFO] wind speed Holtriem: {h_wind} m/s.\tEstimated onshore wind power: {onshore} GW")
        print(f"[INFO] wind speed BorWinAlpha: {b_wind} m/s.\tEstimated offshore wind power: {offshore} GW")
        print(f"[INFO] cloudiness Oldenburg: {cloudiness}%.\tEstimated solar power: {solar} GW")
        print(f"[INFO] estimated conv power: {conv_power} GW")

    return {
        "onshore": onshore,
        "offshore": offshore,
        "solar": solar,
        "conv": conv_power,
        "total": needed_power
    }

def estimate_power_distribution(power = None) -> Dict[str, float]:
    """estimates the current percentage of the onshore, offshore, solar and conventional power in the local grid.
    If the power parameter is not provided, it will automatically fetch the neede data.
    """
    if power == None:
        power = estimate_power()

    return {
        "onshore": power['onshore'] / power['total'],
        "offshore": power['offshore'] / power['total'],
        "solar": power['solar'] / power['total'],
        "conv": power['conv'] / power['total']
    }

def calculate_gCO2_per_kWh(power_distribution = None, log=True):
    """calculates the CO2 emission per kWh Energy. If no parameter is provided, it will automatically
    fetch the data it needs."""
    if power_distribution == None:
        power_distribution = estimate_power_distribution()
    gCO2_per_kWh = power_distribution['conv'] * 800
    if log:
        print(f"[INFO] estimated emission: {gCO2_per_kWh} g CO2 / kWh")
    return gCO2_per_kWh

def get_all_information():
    """performs all calculations and returns all information in a dict. Returns: \n
    {
        'holtriem_weather': full weather_data dict in Holtriem, DE
        'bor_win_weather': full weather_data dict at the BorWinAlpha offshore windpark
        'oldenburg_weather': full weather_data dict in Oldenburg, DE
        'holtriem_wind': wind speed in Holtriem, DE,
        'bor_win_wind': wind speed at the BorWinAlpha offshore windpark
        'cloudiness': cloudiness in percent in Oldenburg, DE
        'power': dict of the absolut current power. Devided into 'onshore', 'offshore', 'solar', 'conv', 'total'
        'power_dist': percentage of the total power. Devided into 'onshore', 'offshore', 'solar', 'conv'
        'gpkwh': gramm CO2 emission per kWh energy
    }"""
    h_weather = request_weather_data(HOLTRIEM_LAT, HOLTRIEM_LON)
    h_wind = get_wind_speed(h_weather)
    b_weather = request_weather_data(BOR_WIN_LAT, BOR_WIN_LON)
    b_wind = get_wind_speed(b_weather)
    o_weather = request_weather_data(OLDENBURG_LAT, OLDENBURG_LON)
    cloudiness = get_cloudiness(o_weather)
    power = estimate_power(holtriem_wind=h_wind, bor_win_wind= b_wind, cloudiness=cloudiness)
    power_dist = estimate_power_distribution(power)
    gpkwh = calculate_gCO2_per_kWh(power_distribution=power_dist)

    return {
        'holtriem_weather': h_weather,
        'bor_win_weather': b_weather,
        'oldenburg_weather': o_weather,
        'holtriem_wind': h_wind,
        'bor_win_wind': b_wind,
        'cloudiness': cloudiness,
        'power': power,
        'power_dist': power_dist,
        'gpkwh': gpkwh
    }


def write_to_file(power):
    """appends power data to /data/data.csv.
    data is stored in the following format time,onshore,offshore,solar,conv,total,gpkwh"""
    gCO2_per_kWh = calculate_gCO2_per_kWh(estimate_power_distribution(power), log=False)

    with open("data/data.csv", "a") as f:
                f.write(','.join((str(datetime.datetime.now()), *[str(a) for a in power.values()], str(gCO2_per_kWh))) + '\n')


if __name__ == "__main__":
    while True:
        try:
            all = get_all_information()
            power = all['power']
            gCO2_per_kWh = all['gpkwh']
            write_to_file(power)

            ampel_value = map_value_clamp(gCO2_per_kWh, 270, 650, 0, 1)
            print(ampel_value)

            rgb_controller.set_ampel(ampel_value)

            sleep(60*5)
        except KeyboardInterrupt:
            rgb_controller.quit()
            break
