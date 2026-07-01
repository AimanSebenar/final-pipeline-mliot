"""
utils/github_push.py
Pushes a local CSV file to a GitHub repository using the GitHub REST API.
No git binary required — uses only the requests library.

Required environment variables (or fill in config/settings.py):
    GITHUB_TOKEN  — personal access token with repo write scope
    GITHUB_USER   — your GitHub username
    GITHUB_REPO   — target repository name
"""

import base64
import logging
import os
from pathlib import Path

import requests

from config.settings import (
    GITHUB_BRANCH,
    GITHUB_REMOTE_PATH,
    GITHUB_REPO,
    GITHUB_TOKEN,
    GITHUB_USER,
)

log = logging.getLogger(__name__)

API_BASE = "https://api.github.com"


def _resolve_token() -> str:
    token = os.getenv("GITHUB_TOKEN") or GITHUB_TOKEN
    if not token:
        raise EnvironmentError(
            "GitHub token not set. Export GITHUB_TOKEN or set it in config/settings.py"
        )
    return token


def _get_file_sha(session: requests.Session, remote_path: str) -> str | None:
    """Return the blob SHA of an existing file, or None if it does not exist."""
    url = f"{API_BASE}/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{remote_path}"
    resp = session.get(url, params={"ref": GITHUB_BRANCH})
    if resp.status_code == 200:
        return resp.json().get("sha")
    return None


def push_to_github(local_path: Path) -> bool:
    """
    Upload *local_path* to the configured GitHub repository.

    Creates the file if it does not exist; updates (replaces) it if it does.

    Args:
        local_path: Path object pointing to the CSV file on disk.

    Returns:
        True on success, False on failure.
    """
    token = _resolve_token()
    user  = os.getenv("GITHUB_USER")  or GITHUB_USER
    repo  = os.getenv("GITHUB_REPO")  or GITHUB_REPO

    if not user or not repo:
        log.error("GITHUB_USER and GITHUB_REPO must be set.")
        return False

    remote_path = GITHUB_REMOTE_PATH.rstrip("/") + "/" + local_path.name

    session = requests.Session()
    session.headers.update({
        "Authorization": f"token {token}",
        "Accept":        "application/vnd.github+json",
    })

    # Encode file content
    content_b64 = base64.b64encode(local_path.read_bytes()).decode()

    # Check if the file already exists (need its SHA to update)
    sha = _get_file_sha(session, remote_path)

    payload = {
        "message": f"data: add {local_path.name}",
        "content": content_b64,
        "branch":  GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha   # required for updates

    url = f"{API_BASE}/repos/{user}/{repo}/contents/{remote_path}"
    resp = session.put(url, json=payload)

    if resp.status_code in (200, 201):
        log.info("Successfully pushed %s → %s/%s/%s", local_path.name, user, repo, remote_path)
        return True
    else:
        log.error("GitHub push failed [%d]: %s", resp.status_code, resp.text)
        return False