"""Base connector interface and resilience helpers."""
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class SourceState(str, Enum):
    HEALTHY = "Healthy"
    WARNING = "Warning"
    CRITICAL = "Critical"
    UNKNOWN = "Unknown"
    UNAVAILABLE = "Unavailable"


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time: Optional[float] = None
        self.open = False

    def record_success(self):
        self.failures = 0
        self.open = False

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.open = True
            logger.warning("Circuit breaker opened")

    def allow_request(self) -> bool:
        if not self.open:
            return True
        if self.last_failure_time and (time.time() - self.last_failure_time) > self.recovery_timeout:
            self.open = False
            self.failures = 0
            return True
        return False


class BaseConnector(ABC):
    def __init__(self, name: str, timeout: int = 15):
        self.name = name
        self.timeout = timeout
        self.circuit = CircuitBreaker()
        self.configured = False

    @abstractmethod
    def _fetch(self) -> Dict[str, Any]:
        """Implement the actual fetch. Should raise on failure."""
        pass

    def fetch_status(self) -> Dict[str, Any]:
        if not self.configured:
            return {"state": SourceState.UNAVAILABLE, "details": {}, "error": "Not configured"}

        if not self.circuit.allow_request():
            return {"state": SourceState.UNAVAILABLE, "details": {}, "error": "Circuit open"}

        try:
            data = self._fetch()
            self.circuit.record_success()
            return {"state": SourceState.HEALTHY, "details": data, "error": None}
        except Exception as e:
            self.circuit.record_failure()
            logger.error(f"{self.name} fetch failed: {e}")
            return {"state": SourceState.UNAVAILABLE, "details": {}, "error": str(e)}
