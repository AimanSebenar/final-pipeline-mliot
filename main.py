"""
main.py
Raspberry Pi 4 - Real-time Occupancy Prediction
Sensors: Motion (PIR), Temperature/Humidity (DHT22), Audio
Sample rate: 10 seconds
Predictions: ML model (Random Forest, .pkl) + rule-based baseline
Output: JSON payload sent to a Node-RED dashboard via HTTP POST
"""

import time
import logging
from datetime import datetime

import RPi.GPIO as GPIO
import adafruit_dht
# import board
from adafruit_blinka.microcontroller.bcm283x.pin import Pin

from config.settings import (
    MOTION_PIN,
    AUDIO_PIN,
    DHT_PIN,
    SAMPLE_INTERVAL_SEC,
    TOTAL_SAMPLES,
    LOG_DIR,
)
from sensors.motion_sensor import read_motion
from sensors.audio_sensor import read_audio
from sensors.dht_sensor import read_dht
from model.ml_predictor import predict_ml
from model.baseline import predict_baseline
from utils.nodered_sender import send_to_nodered
from actuators.relay_led import setup_relay, pulse_led, relay_off


# ── Logging setup ─────────────────────────────────────────────────────────────
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "sensor_log.txt"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MOTION_PIN, GPIO.IN)
    GPIO.setup(AUDIO_PIN, GPIO.IN)
    setup_relay()
    log.info("GPIO initialised (BCM mode). Motion PIN=%d  Audio PIN=%d", MOTION_PIN, AUDIO_PIN)


def collect_sample(dht_device) -> dict:
    """Read all three sensors and return a result dict."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    motion    = read_motion(MOTION_PIN)
    temp, hum = read_dht(dht_device)
    audio     = read_audio(AUDIO_PIN)

    sample = {
        "timestamp":       timestamp,
        "motion_detected": motion,
        "temperature_c":   temp,
        "humidity_pct":    hum,
        "audio_detected":  audio,
    }
    return sample


def build_payload(sample: dict) -> dict:
    """Run both predictors and assemble the JSON payload for Node-RED."""
    ml_pred       = predict_ml(sample)
    baseline_pred = predict_baseline(sample)

    if ml_pred == 1:
        log.info("ML model predicted occupied → pulsing LED for 1s")
        pulse_led()

    payload = {
        "timestamp":            sample["timestamp"],
        "motion_detected":      sample["motion_detected"],
        "temperature_c":        sample["temperature_c"],
        "humidity_pct":         sample["humidity_pct"],
        "audio_detected":       sample["audio_detected"],
        "occupancy_ml":         ml_pred,
        "occupancy_baseline":   baseline_pred,
        "agreement":            ml_pred == baseline_pred,
    }
    return payload


def run():
    dht_device = adafruit_dht.DHT22(Pin(DHT_PIN))

    try:
        setup_gpio()
        log.info(
            "Starting real-time occupancy prediction. Interval=%ds  TotalSamples=%s",
            SAMPLE_INTERVAL_SEC, TOTAL_SAMPLES if TOTAL_SAMPLES else "∞",
        )

        sample_num = 0
        while True:
            sample_num += 1
            loop_start = time.monotonic()

            sample  = collect_sample(dht_device)
            payload = build_payload(sample)

            log.info("Sample %d → %s", sample_num, payload)
            send_to_nodered(payload)

            if TOTAL_SAMPLES and sample_num >= TOTAL_SAMPLES:
                log.info("Reached TOTAL_SAMPLES=%d — stopping.", TOTAL_SAMPLES)
                break

            # Account for time already spent reading sensors / sending HTTP,
            # so samples land close to every SAMPLE_INTERVAL_SEC, not interval + overhead.
            elapsed = time.monotonic() - loop_start
            sleep_for = max(0, SAMPLE_INTERVAL_SEC - elapsed)
            time.sleep(sleep_for)

    except KeyboardInterrupt:
        log.warning("Interrupted by user — shutting down.")

    finally:
        relay_off()
        dht_device.exit()
        GPIO.cleanup()
        log.info("GPIO cleaned up.")


if __name__ == "__main__":
    run()
