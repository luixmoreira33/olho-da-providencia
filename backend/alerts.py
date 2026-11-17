"""Alerts module (Slack / Teams) — v1.1 foundation."""
import requests
import logging
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)


def send_alert(app_name: str, status: str, message: str):
    payload = {
        "text": f"[{status}] {app_name}: {message}",
        "app": app_name,
        "status": status,
    }
    if settings.slack_webhook:
        try:
            requests.post(settings.slack_webhook, json=payload, timeout=5)
        except Exception as e:
            logger.warning(f"Slack alert failed: {e}")
    if settings.teams_webhook:
        try:
            requests.post(settings.teams_webhook, json=payload, timeout=5)
        except Exception as e:
            logger.warning(f"Teams alert failed: {e}")
