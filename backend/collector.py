"""Background collector that periodically fetches from all connectors."""
import logging
import time
from threading import Thread
from typing import Dict, Any

from db import init_db, upsert_app, save_snapshot
from services.base import SourceState
from services.k8s_connector import KubernetesConnector
from services.aws_connector import AWSConnector
from config import settings

logger = logging.getLogger(__name__)


class Collector:
    def __init__(self, interval: int = 60):
        self.interval = interval
        self.running = False
        self._thread: Thread | None = None
        self.last_results: Dict[str, Any] = {}

        # Instantiate resilient connectors
        self.okd = KubernetesConnector(
            "okd", settings.okd_kubeconfig, settings.okd_context,
            settings.okd_namespace, settings.okd_app_label
        )
        self.eks = KubernetesConnector(
            "eks", settings.eks_kubeconfig, settings.eks_context,
            settings.eks_namespace, settings.eks_app_label
        )
        self.aws = AWSConnector(
            settings.aws_region, settings.aws_access_key_id, settings.aws_secret_access_key
        )

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
        results = {
            "okd": self.okd.fetch_status(),
            "eks": self.eks.fetch_status(),
            "aws": self.aws.fetch_status(),
        }
        self.last_results = results

        # Persist simple snapshots (group by discovered names)
        all_names = set()
        for src in results.values():
            details = src.get("details", {})
            if isinstance(details, dict):
                all_names.update(details.keys())

        for name in all_names:
            app_id = upsert_app(name)
            details_for_app = {}
            source_states = {}
            overall = "Healthy"
            for src_name, src_res in results.items():
                d = src_res.get("details", {})
                if name in d:
                    details_for_app[src_name] = d[name]
                    st = d[name].get("status", "Unknown")
                    source_states[src_name] = st
                    if st in ("Critical", "Failed"):
                        overall = "Critical"
                    elif st in ("Warning", "Degraded") and overall != "Critical":
                        overall = "Warning"
                else:
                    source_states[src_name] = src_res.get("state", SourceState.UNAVAILABLE)

            save_snapshot(app_id, overall, details_for_app, source_states)

        logger.info(f"Collector stored snapshots for {len(all_names)} apps")
