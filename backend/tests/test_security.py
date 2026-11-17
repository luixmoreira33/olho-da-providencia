"""Additional tests for security and status logic."""
import pytest
from auth import create_access_token, get_password_hash, verify_password
from services.base import CircuitBreaker, SourceState


def test_password_hash():
    hashed = get_password_hash("secret123")
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong", hashed)


def test_jwt_roundtrip():
    token = create_access_token({"sub": "admin", "role": "admin"})
    assert isinstance(token, str)
    assert len(token) > 20


def test_circuit_breaker_recovery(monkeypatch):
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0)
    cb.record_failure()
    assert not cb.allow_request()
    # force recovery
    cb.last_failure_time = 0
    assert cb.allow_request()
