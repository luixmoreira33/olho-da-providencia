"""Integration-style tests with mocked sources."""
import pytest
from unittest.mock import patch, MagicMock
from db import init_db, upsert_app


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_db()
    yield


def test_aggregate_with_mocked_sources(temp_db):
    with patch("main.okd_client") as okd, \
         patch("main.eks_client") as eks, \
         patch("main.elk_client") as elk, \
         patch("main.dynatrace_client") as dt, \
         patch("main.aws_client") as aws:

        okd.get_applications_status.return_value = {
            "payment-service": {"cluster": "okd", "namespace": "prod", "pods_ready": 3, "pods_desired": 3, "restarts": 0, "status": "Healthy"}
        }
        eks.get_applications_status.return_value = {}
        elk.get_applications_status.return_value = {
            "payment-service": {"error_count_1h": 2, "warn_count_1h": 5, "recent_errors": [], "status": "Healthy"}
        }
        dt.get_applications_status.return_value = {}
        aws.get_ec2_status.return_value = {}
        aws.get_ecs_status.return_value = {}

        from main import aggregate_status
        apps = aggregate_status()
        assert any(a.name == "payment-service" for a in apps)
        app = next(a for a in apps if a.name == "payment-service")
        assert app.overall_status in ("Healthy", "Warning", "Critical")
