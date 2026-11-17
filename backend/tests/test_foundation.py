"""Basic tests for foundation modules."""
import pytest
from db import init_db, upsert_app, save_snapshot, get_recent_snapshots
from services.base import CircuitBreaker, SourceState


def test_circuit_breaker():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
    assert cb.allow_request()
    cb.record_failure()
    cb.record_failure()
    assert not cb.allow_request()
    cb.record_success()
    assert cb.allow_request()


def test_db_snapshot(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_db()
    app_id = upsert_app("test-app")
    save_snapshot(app_id, "Healthy", {"okd": {"status": "Healthy"}}, {"okd": "Healthy"})
    snaps = get_recent_snapshots(app_id)
    assert len(snaps) == 1
    assert snaps[0]["overall_status"] == "Healthy"
