"""
sensors/audio_sensor.py
Reads a digital sound/audio detection module via a GPIO pin.
Most modules (e.g. KY-038, LM393-based) are active-LOW: DO goes LOW when
sound exceeds the on-board threshold potentiometer setting.
Returns True if sound/audio is detected, False otherwise.
"""

import logging
import RPi.GPIO as GPIO

log = logging.getLogger(__name__)


def read_audio(pin: int) -> bool:
    """
    Read the digital output of a sound detection module.
    Active-LOW logic: 0 → sound detected, 1 → quiet.
    """
    try:
        raw = GPIO.input(pin)
        detected = (raw == GPIO.LOW)
        log.debug("Audio pin %d → raw=%d  %s", pin, raw, "DETECTED" if detected else "quiet")
        return detected
    except Exception as exc:
        log.error("Audio sensor read error on pin %d: %s", pin, exc)
        return False
