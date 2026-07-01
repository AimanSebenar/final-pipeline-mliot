"""
model/baseline.py
Simple rule-based ("baseline") occupancy prediction, computed independently
of the ML model. Useful as a sanity-check / comparison point in the dashboard.

This is NOT a trained model — it's a hand-written heuristic.
Edit predict_baseline() if you want a different rule.
"""

import logging

log = logging.getLogger(__name__)


def predict_baseline(sample: dict) -> int:
    """
    Heuristic: room is considered OCCUPIED if motion OR audio is detected.

    Args:
        sample: dict with keys motion_detected, audio_detected (others ignored)

    Returns:
        1 if occupied, 0 if not — same encoding as the ML model's output.
    """
    motion = bool(sample.get("motion_detected"))
    audio  = bool(sample.get("audio_detected"))

    occupied = motion or audio
    prediction = int(occupied)

    log.debug("Baseline rule: motion=%s audio=%s → occupancy=%s", motion, audio, prediction)
    return prediction
