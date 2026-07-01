"""
utils/nodered_sender.py
Sends each prediction result to a Node-RED dashboard via an HTTP POST,
as JSON. Retries on transient failures so a single dropped request
doesn't crash the sampling loop.
"""

import logging
import time

import requests

from config.settings import (
    NODERED_URL,
    NODERED_TIMEOUT_SEC,
    NODERED_RETRY_COUNT,
    NODERED_RETRY_DELAY,
)

log = logging.getLogger(__name__)


def send_to_nodered(payload: dict) -> bool:
    """
    POST a JSON payload to the Node-RED HTTP In node.

    Args:
        payload: dict to be sent as the JSON body.

    Returns:
        True if delivered successfully (HTTP 2xx), False otherwise.
    """
    headers = {"Content-Type": "application/json"}

    for attempt in range(1, NODERED_RETRY_COUNT + 1):
        try:
            resp = requests.post(
                NODERED_URL,
                json=payload,
                headers=headers,
                timeout=NODERED_TIMEOUT_SEC,
            )
            if 200 <= resp.status_code < 300:
                log.info("Sent to Node-RED OK [%d]: %s", resp.status_code, payload)
                return True
            else:
                log.warning(
                    "Node-RED responded [%d] on attempt %d/%d: %s",
                    resp.status_code, attempt, NODERED_RETRY_COUNT, resp.text,
                )
        except requests.exceptions.RequestException as exc:
            log.warning(
                "Node-RED POST failed (attempt %d/%d): %s",
                attempt, NODERED_RETRY_COUNT, exc,
            )

        if attempt < NODERED_RETRY_COUNT:
            time.sleep(NODERED_RETRY_DELAY)

    log.error("Failed to deliver payload to Node-RED after %d attempts: %s", NODERED_RETRY_COUNT, payload)
    return False
