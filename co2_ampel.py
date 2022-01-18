
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

def request_weather_data(city: str):
    with open("KEY.txt") as f:
        key = f.read()
    res = req.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}")
    return json.loads(res.text)

def calculate_ampel_value(weather_data):
    wind_speed = weather_data['wind']['speed']
    sun = 100 - weather_data['clouds']['all']

    wind_co2 = map_value_clamp(wind_speed, 0, 30, 0.5, 0)
    sun_co2  = map_value_clamp(sun, 40, 100, 0.5, 0)
    
    print(f"sun: {sun}\twind: {wind_speed}")

    return wind_co2 + sun_co2


while True:
    try:
        weather_data = request_weather_data('Oldenburg')
        ampel_value = calculate_ampel_value(weather_data)
        
        if leds_present:
            rgb_controller.set_ampel(ampel_value)

        sleep(60)
    except KeyboardInterrupt:
        if leds_present:
            rgb_controller.quit()
        break
