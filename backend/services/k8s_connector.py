"""Resilient Kubernetes connector (OKD / EKS)."""
from typing import Dict, Optional
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import logging

from services.base import BaseConnector, SourceState

logger = logging.getLogger(__name__)


class KubernetesConnector(BaseConnector):
    def __init__(
        self,
        name: str,
        kubeconfig: Optional[str],
        context: Optional[str],
        namespace: str,
        app_label: str,
    ):
        super().__init__(name, timeout=20)
        self.namespace = namespace
        self.app_label = app_label
        self.apps_v1 = None
        self.core_v1 = None

        try:
            if kubeconfig:
                config.load_kube_config(config_file=kubeconfig, context=context)
            else:
                try:
                    config.load_incluster_config()
                except Exception:
                    config.load_kube_config(context=context)
            self.apps_v1 = client.AppsV1Api()
            self.core_v1 = client.CoreV1Api()
            self.configured = True
            logger.info(f"{name} Kubernetes connector ready")
        except Exception as e:
            logger.warning(f"{name} not configured: {e}")

    def _fetch(self) -> Dict:
        if not self.apps_v1:
            raise RuntimeError("Client not initialized")

        deployments = self.apps_v1.list_namespaced_deployment(namespace=self.namespace)
        result = {}
        for dep in deployments.items:
            labels = dep.metadata.labels or {}
            app_name = labels.get(self.app_label) or dep.metadata.name
            ready = dep.status.ready_replicas or 0
            desired = dep.spec.replicas or 0
            status = "Healthy" if ready == desired and desired > 0 else ("Warning" if ready > 0 else "Critical")
            result[app_name] = {
                "cluster": self.name,
                "namespace": self.namespace,
                "pods_ready": ready,
                "pods_desired": desired,
                "restarts": 0,  # would require pod listing for exact count
                "status": status,
            }
        return result
