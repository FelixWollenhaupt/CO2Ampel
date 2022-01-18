
# weather_data = {'base': 'stations',
#  'clouds': {'all': 53},
#  'cod': 200,
#  'coord': {'lat': 53.1667, 'lon': 8.2},
#  'dt': 1642432315,
#  'id': 2857458,
#  'main': {'feels_like': 276.32,
#           'grnd_level': 1029,
#           'humidity': 81,
#           'pressure': 1030,
#           'sea_level': 1030,
#           'temp': 280.24,
#           'temp_max': 281.33,
#           'temp_min': 279.31},
#  'name': 'Oldenburg',
#  'sys': {'country': 'DE',
#          'id': 2010542,
#          'sunrise': 1642404708,
#          'sunset': 1642434135,
#          'type': 2},
#  'timezone': 3600,
#  'visibility': 10000,
#  'weather': [{'description': 'broken clouds',
#               'icon': '04d',
#               'id': 803,
#               'main': 'Clouds'}],
#  'wind': {'deg': 334, 'gust': 12.68, 'speed': 7.08}}


import requests as req
import json
from time import sleep

import rgb_controller

def map_value(x, a, b, c, d):
    return ((c - d) * (x - a)) / (a - b) + c

def map_value_clamp(x, a, b, c, d):
    v = map_value(x, a, b, c, d)
    if v < c and v < d:
        return min(c, d)
    elif v > c and v > d:
        return max(c, d)
    return v


key = "KEY"
city = "Oldenburg"

while True:
    res = req.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}")

    weather_data = json.loads(res.text)

    wind_speed = weather_data['wind']['speed']
    sun = 100 - weather_data['clouds']['all']

    print(f"wind speed: {wind_speed} m/s\tsun: {sun}%")

    wind = map_value_clamp(wind_speed, 0, 10, 0, 0.5)
    sun  = map_value_clamp(sun, 0, 100, 0, 0.5)

    total = wind + sun

    rgb_controller.set_ampel(total)

    sleep(60)