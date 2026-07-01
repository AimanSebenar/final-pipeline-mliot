"""
sensors/motion_sensor.py
Reads a PIR (passive infrared) motion sensor via a digital GPIO pin.
Returns True if motion is detected, False otherwise.
"""

import logging
import RPi.GPIO as GPIO

log = logging.getLogger(__name__)


def read_motion(pin: int) -> bool:
    """
    Read the digital output of a PIR sensor.
    Most PIR modules output HIGH (1) when motion is detected, LOW (0) when idle.
    """
    try:
        state = GPIO.input(pin)
        detected = bool(state)
        log.debug("Motion pin %d → %s", pin, "DETECTED" if detected else "clear")
        return detected
    except Exception as exc:
        log.error("Motion sensor read error on pin %d: %s", pin, exc)
        return False
