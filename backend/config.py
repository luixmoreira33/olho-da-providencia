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

    # AWS (EC2 + ECS)
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    aws_access_key_id: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    # If not set, uses default credential chain (IAM role, env, ~/.aws/credentials)

    # Admin filter (comma-separated names to show; empty = show all discovered)
    visible_resources: Optional[str] = os.getenv("VISIBLE_RESOURCES")

    # Deep links (configurable base URLs)
    kibana_url: Optional[str] = os.getenv("KIBANA_URL", "https://kibana.example.com")
    dynatrace_ui_url: Optional[str] = os.getenv("DYNATRACE_UI_URL")
    aws_console_url: str = os.getenv("AWS_CONSOLE_URL", "https://console.aws.amazon.com")
    okd_console_url: Optional[str] = os.getenv("OKD_CONSOLE_URL")
    eks_console_url: Optional[str] = os.getenv("EKS_CONSOLE_URL")

    # Alerts (v1.1)
    slack_webhook: Optional[str] = os.getenv("SLACK_WEBHOOK_URL")
    teams_webhook: Optional[str] = os.getenv("TEAMS_WEBHOOK_URL")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
