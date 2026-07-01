from pathlib import Path

# ── GPIO pin numbers (BCM numbering) ──────────────────────────────────────────
MOTION_PIN = 17          # PIR motion sensor digital output
AUDIO_PIN  = 23          # Sound/audio sensor digital output
DHT_PIN    = 4           # DHT22 data pin (also set on board.D4)
RELAY_PIN  = 22          # Relay controlling the LED

# ── Sampling ───────────────────────────────────────────────────────────────────
SAMPLE_INTERVAL_SEC = 10        # 10 seconds between samples
TOTAL_SAMPLES        = 0        # 0 = run forever; set a number to stop after N samples

# DHT22 sensors are physically limited to ~1 reading every 2 seconds.
# At a 10 s sample rate this is fine.

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR      = PROJECT_ROOT / "logs"
MODEL_PATH   = PROJECT_ROOT / "model" / "occupancy_model.pkl"

# ── Node-RED dashboard ─────────────────────────────────────────────────────────
# URL of the HTTP In node configured in your Node-RED flow.
NODERED_URL          = "http://IP_ADDRESS/api/sensors"
NODERED_TIMEOUT_SEC  = 5
NODERED_RETRY_COUNT  = 3
NODERED_RETRY_DELAY  = 2

# ── Baseline rule-based prediction ────────────────────────────────────────────
# Simple heuristic: occupied if motion OR audio is detected.
# (Used as a sanity-check / comparison point against the ML model.)
BASELINE_RULE = "motion_or_audio"   # see model/baseline.py

# ── Relay / LED indicator ──────────────────────────────────────────────────────
# Pulses ON for RELAY_PULSE_SEC whenever the ML model predicts occupied (True).
RELAY_ACTIVE_LOW =False   # most relay modules energise on a LOW signal — flip if yours is active-HIGH
RELAY_PULSE_SEC  = 1      # seconds the LED stays on per trigger
