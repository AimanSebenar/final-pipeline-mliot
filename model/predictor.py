"""
model/predictor.py
Loads the pickled Random Forest model once and exposes a predict() function
that takes the latest sensor reading and returns an occupancy prediction.
"""

import logging
import joblib
import numpy as np
from pathlib import Path

log = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).resolve().parent / "occupancy_model.pkl"

# Feature order MUST match the order used when the model was trained.
FEATURE_ORDER = ["motion_detected", "temperature_c", "humidity_pct", "audio_detected"]

_model = None  # loaded lazily, once


def load_model():
    global _model
    if _model is None:
        log.info("Loading model from %s", MODEL_PATH)
        _model = joblib.load(MODEL_PATH)
    return _model


def predict_occupancy(sample: dict) -> int:
    """
    Args:
        sample: dict with keys matching FEATURE_ORDER
                (motion_detected, temperature_c, humidity_pct, audio_detected)

    Returns:
        Predicted class (e.g. 0 = unoccupied, 1 = occupied)
    """
    model = load_model()

    # Convert booleans to int, build feature vector in correct order
    features = [
        int(sample["motion_detected"]),
        sample["temperature_c"] if sample["temperature_c"] is not None else 0.0,
        sample["humidity_pct"] if sample["humidity_pct"] is not None else 0.0,
        int(sample["audio_detected"]),
    ]

    X = np.array(features).reshape(1, -1)
    prediction = model.predict(X)[0]

    log.info("Prediction input=%s → occupancy=%s", features, prediction)
    return int(prediction)
