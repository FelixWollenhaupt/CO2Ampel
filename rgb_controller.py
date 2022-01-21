try:
    import pigpio
    _leds_existing = True
except ImportError:
    print("[WARNING] could not use GPIOs. Did you install pigpio")
    _leds_existing = False

from typing import Collection
from time import sleep

pi = pigpio.pi() if _leds_existing else None

PIN_RED = 17
PIN_GREEN = 22
PIN_BLUE = 24

def _ensure_valid_brightness(brightness: int) -> int:
    """clamps the parameter brightness to the range 0 - 255"""
    if brightness > 255:
        return 255
    elif brightness < 0:
        return 0
    return brightness

def _lerp(a: float, b: float, amt: float) -> float:
    """linearly interpolates between a and b by the amount amt"""
    return a * (1 - amt) + b * amt 

def _lerp_color(color_a: Collection, color_b: Collection, amt: float) -> Collection:
    """interpolates between two given colors by the amount amt"""
    ret = [_lerp(a, b, amt) for a, b in zip(color_a, color_b)]
    return ret

def set_color(color: Collection) -> None:
    """sets leds to the given color"""
    if _leds_existing:
        pi.set_PWM_dutycycle(PIN_RED, _ensure_valid_brightness(color[0]))
        pi.set_PWM_dutycycle(PIN_GREEN, _ensure_valid_brightness(color[1]))
        pi.set_PWM_dutycycle(PIN_BLUE, _ensure_valid_brightness(color[2]))

def clear() -> None:
    """clears leds"""
    set_color((0, 0, 0))

def set_ampel(amount: float) -> None:
    """lights up leds on a scale from green to red according to the parameter amount.
        0 -> green, 1 -> red"""
    if amount > 1:
        raise ValueError("Ampel amount above 1")
    elif amount < 0:
        raise ValueError("Ampel amount below 0")

    set_color(_lerp_color((0, 255, 0), (255, 0, 0), amount))

def quit() -> None:
    """clears the leds and stops the controll"""
    if _leds_existing:
        clear()
        pi.stop()


if __name__ == "__main__":
    set_ampel(0.8)
    
    sleep(2)

    quit()