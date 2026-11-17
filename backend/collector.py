"""Background collector that periodically fetches from all connectors."""
import logging
import time
from threading import Thread
from typing import Dict

from db import init_db, upsert_app, save_snapshot
from services.base import SourceState

logger = logging.getLogger(__name__)


class Collector:
    def __init__(self, interval: int = 60):
        self.interval = interval
        self.running = False
        self._thread: Thread | None = None
        self.last_results: Dict = {}

    def start(self):
        if self.running:
            return
        init_db()
        self.running = True
        self._thread = Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info("Collector started")

    def stop(self):
        self.running = False

    def _loop(self):
        while self.running:
            try:
                self.collect()
            except Exception as e:
                logger.error(f"Collector error: {e}")
            time.sleep(self.interval)

    def collect(self):
        """Override or inject connectors here. Placeholder that stores mock-friendly structure."""
        # In real implementation this will call the resilient connectors
        # and persist snapshots. For now it is the hook.
        logger.debug("Collector tick")
