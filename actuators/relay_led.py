"""
actuators/relay_led.py
Drives an LED via a relay module connected to a GPIO pin.
Pulses the relay ON for 1 second whenever called — runs in a background
thread so it never blocks the main 10-second sampling loop.

Most relay modules are active-LOW: a LOW signal energises the relay (LED ON).
If yours is active-HIGH instead, flip RELAY_ACTIVE_LOW to False in config/settings.py.
"""

import logging
import threading
import time

import RPi.GPIO as GPIO

from config.settings import RELAY_PIN, RELAY_ACTIVE_LOW, RELAY_PULSE_SEC

log = logging.getLogger(__name__)

_ON  = GPIO.LOW if RELAY_ACTIVE_LOW else GPIO.HIGH
_OFF = GPIO.HIGH if RELAY_ACTIVE_LOW else GPIO.LOW

_lock = threading.Lock()  # prevents overlapping pulses from stacking oddly


def setup_relay():
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    GPIO.output(RELAY_PIN, _OFF)
    log.info("Relay/LED initialised on GPIO %d (active_low=%s)", RELAY_PIN, RELAY_ACTIVE_LOW)


def _pulse_worker():
    with _lock:
        GPIO.output(RELAY_PIN, _ON)
        log.debug("Relay ON")
        time.sleep(RELAY_PULSE_SEC)
        GPIO.output(RELAY_PIN, _OFF)
        log.debug("Relay OFF")


def pulse_led():
    """
    Turn the LED on for RELAY_PULSE_SEC (default 1s), then off — without
    blocking the caller. Safe to call once per sample loop.
    """
    threading.Thread(target=_pulse_worker, daemon=True).start()


def relay_off():
    """Force the relay off immediately (used on shutdown)."""
    GPIO.output(RELAY_PIN, _OFF)
