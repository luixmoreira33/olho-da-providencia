import requests
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class DynatraceClient:
    def __init__(self, url: Optional[str], token: Optional[str]):
        self.url = url.rstrip("/") if url else None
        self.token = token
        self.configured = bool(self.url and self.token)
        self.headers = {"Authorization": f"Api-Token {token}"} if token else {}

        if self.configured:
            logger.info("Dynatrace client configured")
        else:
            logger.warning("Dynatrace URL or token missing")

    def get_applications_status(self, app_names: Optional[List[str]] = None) -> Dict[str, dict]:
        if not self.configured:
            return {}

        result = {}
        try:
            # Get open problems
            params = {
                "problemSelector": 'status("OPEN")',
                "pageSize": 100
            }
            resp = requests.get(
                f"{self.url}/api/v2/problems",
                headers=self.headers,
                params=params,
                timeout=15
            )
            resp.raise_for_status()
            problems = resp.json().get("problems", [])

            # Group problems by entity / service name (simplified matching)
            problem_map = {}
            for p in problems:
                for entity in p.get("affectedEntities", []):
                    name = entity.get("name", "")
                    # Try to match app name
                    for app in (app_names or []):
                        if app.lower() in name.lower():
                            problem_map.setdefault(app, []).append(p)

            # For each app (or from problems), build status
            apps_to_check = set(app_names or []) | set(problem_map.keys())

            for app in apps_to_check:
                open_count = len(problem_map.get(app, []))
                # Simple health based on open problems (you can expand with metrics API)
                status = "Healthy" if open_count == 0 else ("Warning" if open_count == 1 else "Critical")
                health_state = "HEALTHY" if open_count == 0 else "UNHEALTHY"

                result[app] = {
                    "open_problems": open_count,
                    "health_state": health_state,
                    "error_rate_percent": 0.0,  # placeholder - expand with metrics if needed
                    "response_time_ms": 0.0,
                    "status": status
                }

            # Optional: try to fetch basic service metrics (best-effort)
            try:
                metrics_resp = requests.get(
                    f"{self.url}/api/v2/metrics/query",
                    headers=self.headers,
                    params={
                        "metricSelector": "builtin:service.errors.server.rate,builtin:service.response.time",
                        "resolution": "1h"
                    },
                    timeout=15
                )
                if metrics_resp.ok:
                    # Enrich result if possible (simplified)
                    pass
            except Exception:
                pass

        except Exception as e:
            logger.error(f"Error querying Dynatrace: {e}")

        return result
