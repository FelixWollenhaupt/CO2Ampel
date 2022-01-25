import json
import requests as req

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


KEY = None
def load_api_key():
    global KEY
    if KEY == None:
        with open("KEY.txt") as f:
            KEY = f.read().rstrip()
    return KEY

def request_weather_data(lat, lon):
    """Requests weather data using the openweathermap api."""
    key = load_api_key()
    print(f"[INFO] requesting weather at {lat}, {lon}")
    res = req.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}")
    return json.loads(res.text)