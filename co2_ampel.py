import requests as req
import json
from time import sleep
import datetime
from math import sin, pi, e


try:
    import rgb_controller
    leds_present = True
except ImportError:
    print("could not import the rgb_controller or one of its dependencies")
    leds_present = False

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
OLDENBURG_LAT   = 51.165691
OLDENBURG_LON   = 10.451526

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
    print(f"[INFO] requesting weather data at {lat}, {lon}")
    res = req.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}")
    return json.loads(res.text)

def get_wind_speed(lat, lon):
    weather_data = request_weather_data(lat, lon)
    return weather_data['wind']['speed']

def get_cloundiness(lat, lon):
    weather_data = request_weather_data(lat, lon)
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
        return force_non_negative(map_value(wind_speed, 4.65, 9.89, 0.732, 5.465))
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
    factor = list(SOLAR_FACTOR.values())[date.month - 1]
    return factor * (1 - cloudiness / 100 + 0.2) * SOLAR_CONSTANT * force_non_negative(sin(2 * pi / 24 * ((date.hour + date.minute / 60) - 6)))

def estimate_current_solar_power(cloudiness):
    return estimate_solar_power(datetime.datetime.now(), cloudiness)

def estimate_power():
    needed_power = estimate_currently_needed_power()

    wind = get_wind_speed(HOLTRIEM_LAT, HOLTRIEM_LON)
    onshore = estimate_onshore_wind_power(wind)
    print(f"[INFO] wind speed Holtriem: {wind} m/s. Estimated onshore wind power: {onshore} GW")

    wind = get_wind_speed(BOR_WIN_LAT, BOR_WIN_LON)
    offshore = estimate_offshore_wind_power(wind)
    print(f"[INFO] wind speed BorWinAlpha: {wind} m/s. Estimated offshore wind power: {offshore} GW")

    cloudiness = get_cloundiness(OLDENBURG_LAT, OLDENBURG_LON)
    solar = estimate_current_solar_power(cloudiness)
    print(f"[INFO] cloundiness Oldenburg: {cloudiness}. Estimated solar power: {solar}")

    renewable_power_supply = onshore + offshore + solar

    conv_power = c if (c := needed_power - renewable_power_supply) > 0 else 0

    return {
        "onshore": onshore,
        "offshore": offshore,
        "solar": solar,
        "conv": conv_power,
        "total": needed_power
    }

def estimate_power_distribution():
    power = estimate_power()

    return {
        "onshore": power['onshore'] / power['total'],
        "offshore": power['offshore'] / power['total'],
        "solar": power['solar'] / power['total'],
        "conv": power['conv'] / power['total']
    }

def calculate_gCO2_per_kWh():
    gCO2_per_kWh = estimate_power_distribution()['conv'] * 800
    print(f"[INFO] estimated emission: {gCO2_per_kWh} g CO2 / kWh")
    return gCO2_per_kWh

while True:
    try:
        gCO2_per_kWh = calculate_gCO2_per_kWh()

        ampel_value = map_value_clamp(gCO2_per_kWh, 270, 650, 0, 1)

        if leds_present:
            rgb_controller.set_ampel(ampel_value)

        sleep(60)
    except KeyboardInterrupt:
        if leds_present:
            rgb_controller.quit()
        break
