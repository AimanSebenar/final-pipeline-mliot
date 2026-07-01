"""
utils/csv_writer.py
Handles CSV file initialisation and row-by-row writing.
"""

import csv
import logging
from pathlib import Path

log = logging.getLogger(__name__)

FIELDNAMES = ["timestamp", "motion_detected", "temperature_c", "humidity_pct", "audio_detected", "occupancy_predicted"]


def init_csv(path: Path) -> None:
    """Create the CSV file and write the header row."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
    log.info("CSV initialised → %s", path)


def write_row(path: Path, data: dict) -> None:
    """Append a single sample row to the CSV."""
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(data)
    log.debug("Row written: %s", data)
