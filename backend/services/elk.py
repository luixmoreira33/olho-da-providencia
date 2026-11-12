from elasticsearch import Elasticsearch
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ElkClient:
    def __init__(self, url: Optional[str], user: Optional[str], password: Optional[str], api_key: Optional[str],
                 index_pattern: str, service_field: str, time_range: str):
        self.index_pattern = index_pattern
        self.service_field = service_field
        self.time_range = time_range
        self.es = None
        self.configured = False

        if not url:
            return

        try:
            if api_key:
                self.es = Elasticsearch(url, api_key=api_key, verify_certs=False)
            elif user and password:
                self.es = Elasticsearch(url, basic_auth=(user, password), verify_certs=False)
            else:
                self.es = Elasticsearch(url, verify_certs=False)

            # Test connection
            if self.es.ping():
                self.configured = True
                logger.info("Elasticsearch client configured successfully")
            else:
                logger.warning("Elasticsearch ping failed")
        except Exception as e:
            logger.warning(f"Failed to configure Elasticsearch client: {e}")

    def get_applications_status(self, app_names: Optional[List[str]] = None) -> Dict[str, dict]:
        if not self.configured:
            return {}

        result = {}
        try:
            # Aggregation query for error/warn counts by service
            query = {
                "size": 0,
                "query": {
                    "bool": {
                        "filter": [
                            {"range": {"@timestamp": {"gte": self.time_range}}},
                            {"terms": {"log.level": ["ERROR", "WARN", "error", "warn"]}}
                        ]
                    }
                },
                "aggs": {
                    "by_service": {
                        "terms": {"field": f"{self.service_field}.keyword", "size": 100},
                        "aggs": {
                            "errors": {
                                "filter": {"terms": {"log.level": ["ERROR", "error"]}}
                            },
                            "warns": {
                                "filter": {"terms": {"log.level": ["WARN", "warn"]}}
                            },
                            "recent_errors": {
                                "top_hits": {
                                    "size": 3,
                                    "sort": [{"@timestamp": "desc"}],
                                    "_source": ["message", "log.level"]
                                }
                            }
                        }
                    }
                }
            }

            if app_names:
                query["query"]["bool"]["filter"].append({
                    "terms": {f"{self.service_field}.keyword": app_names}
                })

            resp = self.es.search(index=self.index_pattern, body=query)
            buckets = resp.get("aggregations", {}).get("by_service", {}).get("buckets", [])

            for bucket in buckets:
                app = bucket["key"]
                errors = bucket["errors"]["doc_count"]
                warns = bucket["warns"]["doc_count"]
                recent = []
                for hit in bucket["recent_errors"]["hits"]["hits"]:
                    src = hit["_source"]
                    msg = src.get("message", "No message")
                    recent.append(f"{src.get('log.level', 'ERROR')}: {msg[:200]}")

                status = "Healthy" if errors < 5 else ("Warning" if errors < 15 else "Critical")
                result[app] = {
                    "error_count_1h": errors,
                    "warn_count_1h": warns,
                    "recent_errors": recent,
                    "status": status
                }
        except Exception as e:
            logger.error(f"Error querying Elasticsearch: {e}")

        return result
