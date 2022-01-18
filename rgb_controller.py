

import pigpio
from time import sleep

pi = pigpio.pi()

PIN_RED = 17
PIN_GREEN = 22
PIN_BLUE = 24

def _ensure_valid_brightness(brightness):
    if brightness > 255:
        return 255
    elif brightness < 0:
        return 0
    return brightness

def _lerp(a, b, amt):
    return a * (1 - amt) + b * amt 

def _lerp_color(color_a, color_b, amt):
    ret = [_lerp(a, b, amt) for a, b in zip(color_a, color_b)]
    return ret

def set_color(color):
    pi.set_PWM_dutycycle(PIN_RED, _ensure_valid_brightness(color[0]))
    pi.set_PWM_dutycycle(PIN_GREEN, _ensure_valid_brightness(color[1]))
    pi.set_PWM_dutycycle(PIN_BLUE, _ensure_valid_brightness(color[2]))

def clear():
    set_color((0, 0, 0))

def set_ampel(amount):
    if amount > 1:
        raise ValueError("Ampel amount above 1")
    elif amount < 0:
        raise ValueError("Ampel amount below 0")

    set_color(_lerp_color((0, 255, 0), (255, 0, 0), amount))

if __name__ == "__main__":
    for i in range(100):
        l = i / 100
        set_ampel(l)
        sleep(0.05)

    sleep(1)

    clear()

    pi.stop()


