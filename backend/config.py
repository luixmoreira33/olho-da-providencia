import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Kubernetes / OKD
    okd_kubeconfig: Optional[str] = os.getenv("OKD_KUBECONFIG")  # path to kubeconfig
    okd_context: Optional[str] = os.getenv("OKD_CONTEXT")
    okd_namespace: str = os.getenv("OKD_NAMESPACE", "default")
    okd_app_label: str = os.getenv("OKD_APP_LABEL", "app")  # label key used to identify apps

    # Kubernetes / EKS
    eks_kubeconfig: Optional[str] = os.getenv("EKS_KUBECONFIG")
    eks_context: Optional[str] = os.getenv("EKS_CONTEXT")
    eks_namespace: str = os.getenv("EKS_NAMESPACE", "default")
    eks_app_label: str = os.getenv("EKS_APP_LABEL", "app")

    # ELK / Elasticsearch
    elk_url: Optional[str] = os.getenv("ELK_URL")  # e.g. https://es.example.com:9200
    elk_user: Optional[str] = os.getenv("ELK_USER")
    elk_password: Optional[str] = os.getenv("ELK_PASSWORD")
    elk_api_key: Optional[str] = os.getenv("ELK_API_KEY")  # preferred if available
    elk_index_pattern: str = os.getenv("ELK_INDEX_PATTERN", "logs-*")
    elk_service_field: str = os.getenv("ELK_SERVICE_FIELD", "service.name")  # or kubernetes.labels.app, etc.
    elk_time_range: str = os.getenv("ELK_TIME_RANGE", "now-1h")

    # Dynatrace
    dynatrace_url: Optional[str] = os.getenv("DYNATRACE_URL")  # e.g. https://xxx.live.dynatrace.com
    dynatrace_token: Optional[str] = os.getenv("DYNATRACE_TOKEN")
    dynatrace_entity_selector: str = os.getenv("DYNATRACE_ENTITY_SELECTOR", "type(SERVICE)")

    # AI Insight (OpenAI-compatible: Grok, OpenAI, Ollama, etc.)
    ai_enabled: bool = os.getenv("AI_ENABLED", "false").lower() == "true"
    ai_base_url: Optional[str] = os.getenv("AI_BASE_URL")  # e.g. https://api.x.ai/v1 or http://localhost:11434/v1
    ai_api_key: Optional[str] = os.getenv("AI_API_KEY")
    ai_model: str = os.getenv("AI_MODEL", "grok-beta")

    # General
    app_list: Optional[str] = os.getenv("APP_LIST")  # comma-separated explicit list of apps (optional)
    use_mock_if_unconfigured: bool = os.getenv("USE_MOCK_IF_UNCONFIGURED", "true").lower() == "true"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
