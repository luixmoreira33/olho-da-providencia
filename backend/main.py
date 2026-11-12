from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import logging

from config import settings
from services.k8s import KubernetesClient
from services.elk import ElkClient
from services.dynatrace import DynatraceClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Status Dashboard API", description="Painel unificado OKD / EKS / ELK / Dynatrace")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models (same as before)
class K8sStatus(BaseModel):
    cluster: str
    namespace: str
    pods_ready: int
    pods_desired: int
    restarts: int
    status: str
    last_updated: Optional[str] = None

class ElkStatus(BaseModel):
    error_count_1h: int
    warn_count_1h: int
    recent_errors: List[str]
    status: str

class DynatraceStatus(BaseModel):
    open_problems: int
    health_state: str
    error_rate_percent: float
    response_time_ms: float
    status: str

class ApplicationStatus(BaseModel):
    name: str
    overall_status: str
    k8s_okd: Optional[K8sStatus] = None
    k8s_eks: Optional[K8sStatus] = None
    elk: Optional[ElkStatus] = None
    dynatrace: Optional[DynatraceStatus] = None
    summary: str

# Initialize clients once
okd_client = KubernetesClient(
    settings.okd_kubeconfig, settings.okd_context,
    settings.okd_namespace, settings.okd_app_label, "okd"
)
eks_client = KubernetesClient(
    settings.eks_kubeconfig, settings.eks_context,
    settings.eks_namespace, settings.eks_app_label, "eks"
)
elk_client = ElkClient(
    settings.elk_url, settings.elk_user, settings.elk_password,
    settings.elk_api_key, settings.elk_index_pattern,
    settings.elk_service_field, settings.elk_time_range
)
dynatrace_client = DynatraceClient(settings.dynatrace_url, settings.dynatrace_token)


def generate_mock_apps() -> List[ApplicationStatus]:
    """Fallback mock data when sources are not configured."""
    from random import choice, randint, uniform
    apps = ["payment-service", "user-api", "order-processor", "notification-service", "inventory-api", "auth-gateway"]
    result = []
    now = datetime.utcnow().isoformat() + "Z"
    for name in apps:
        ready = choice([3, 3, 2, 1])
        okd = K8sStatus(cluster="okd", namespace="prod", pods_ready=ready, pods_desired=3,
                        restarts=randint(0, 4), status="Healthy" if ready == 3 else "Degraded", last_updated=now) if choice([True, False]) else None
        ready_e = choice([4, 4, 3])
        eks = K8sStatus(cluster="eks", namespace="production", pods_ready=ready_e, pods_desired=4,
                        restarts=randint(0, 2), status="Healthy" if ready_e == 4 else "Degraded", last_updated=now) if choice([True, False]) else None
        errors = randint(0, 20)
        elk = ElkStatus(error_count_1h=errors, warn_count_1h=randint(0, 30),
                        recent_errors=[f"ERROR: sample error in {name}"] if errors else [],
                        status="Healthy" if errors < 5 else "Warning" if errors < 12 else "Critical")
        problems = choice([0, 0, 1])
        dt = DynatraceStatus(open_problems=problems, health_state="HEALTHY" if problems == 0 else "UNHEALTHY",
                             error_rate_percent=round(uniform(0.1, 5), 2), response_time_ms=round(uniform(40, 600), 1),
                             status="Healthy" if problems == 0 else "Warning")
        statuses = [s.status for s in [okd, eks, elk, dt] if s]
        if any(s in ("Critical", "Failed") for s in statuses):
            overall, summary = "Critical", "Problemas críticos detectados."
        elif any(s in ("Warning", "Degraded") for s in statuses):
            overall, summary = "Warning", "Alguns alertas ou degradação."
        else:
            overall, summary = "Healthy", "Tudo operacional."
        result.append(ApplicationStatus(name=name, overall_status=overall, k8s_okd=okd, k8s_eks=eks, elk=elk, dynatrace=dt, summary=summary))
    return result


def aggregate_status() -> List[ApplicationStatus]:
    """Aggregate real data from all sources. Falls back to mock if nothing configured."""
    okd_data = okd_client.get_applications_status()
    eks_data = eks_client.get_applications_status()
    # Discover app names from K8s first
    all_apps = set(okd_data.keys()) | set(eks_data.keys())

    explicit_apps = None
    if settings.app_list:
        explicit_apps = [a.strip() for a in settings.app_list.split(",") if a.strip()]
        all_apps |= set(explicit_apps)

    elk_data = elk_client.get_applications_status(list(all_apps) if all_apps else None)
    dt_data = dynatrace_client.get_applications_status(list(all_apps) if all_apps else None)

    all_apps |= set(elk_data.keys()) | set(dt_data.keys())

    if not all_apps and settings.use_mock_if_unconfigured:
        logger.info("No real data sources configured or returning data — using mock")
        return generate_mock_apps()

    result = []
    for name in sorted(all_apps):
        okd = K8sStatus(**okd_data[name]) if name in okd_data else None
        eks = K8sStatus(**eks_data[name]) if name in eks_data else None
        elk = ElkStatus(**elk_data[name]) if name in elk_data else None
        dt = DynatraceStatus(**dt_data[name]) if name in dt_data else None

        statuses = []
        if okd: statuses.append(okd.status)
        if eks: statuses.append(eks.status)
        if elk: statuses.append(elk.status)
        if dt: statuses.append(dt.status)

        if not statuses:
            continue

        if any(s in ("Critical", "Failed") for s in statuses):
            overall = "Critical"
            summary = "Problemas críticos detectados em um ou mais sistemas."
        elif any(s in ("Warning", "Degraded") for s in statuses):
            overall = "Warning"
            summary = "Alguns alertas ou degradação. Verifique os detalhes."
        else:
            overall = "Healthy"
            summary = "Tudo operacional. Sem problemas relevantes."

        result.append(ApplicationStatus(
            name=name,
            overall_status=overall,
            k8s_okd=okd,
            k8s_eks=eks,
            elk=elk,
            dynatrace=dt,
            summary=summary
        ))
    return result


@app.get("/")
def root():
    sources = {
        "okd": okd_client.configured,
        "eks": eks_client.configured,
        "elk": elk_client.configured,
        "dynatrace": dynatrace_client.configured
    }
    return {
        "message": "Status Dashboard API - OKD / EKS / ELK / Dynatrace",
        "sources_configured": sources,
        "docs": "/docs"
    }

@app.get("/api/applications", response_model=List[ApplicationStatus])
def get_applications():
    return aggregate_status()

@app.get("/api/applications/{app_name}", response_model=ApplicationStatus)
def get_application(app_name: str):
    apps = aggregate_status()
    for a in apps:
        if a.name == app_name:
            return a
    raise HTTPException(status_code=404, detail="Aplicação não encontrada")

@app.get("/api/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
