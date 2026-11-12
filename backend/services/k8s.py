from kubernetes import client, config
from kubernetes.client.rest import ApiException
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class KubernetesClient:
    def __init__(self, kubeconfig: Optional[str], context: Optional[str], namespace: str, app_label: str, cluster_name: str):
        self.namespace = namespace
        self.app_label = app_label
        self.cluster_name = cluster_name
        self.apps_v1 = None
        self.core_v1 = None
        self.configured = False

        try:
            if kubeconfig:
                config.load_kube_config(config_file=kubeconfig, context=context)
            else:
                # Try in-cluster or default
                try:
                    config.load_incluster_config()
                except Exception:
                    config.load_kube_config(context=context)
            self.apps_v1 = client.AppsV1Api()
            self.core_v1 = client.CoreV1Api()
            self.configured = True
            logger.info(f"{cluster_name} Kubernetes client configured successfully")
        except Exception as e:
            logger.warning(f"Failed to configure {cluster_name} client: {e}")

    def get_applications_status(self) -> Dict[str, dict]:
        if not self.configured:
            return {}

        result = {}
        try:
            # Get deployments
            deployments = self.apps_v1.list_namespaced_deployment(namespace=self.namespace)
            for dep in deployments.items:
                labels = dep.metadata.labels or {}
                app_name = labels.get(self.app_label) or dep.metadata.name
                ready = dep.status.ready_replicas or 0
                desired = dep.spec.replicas or 0
                status = "Healthy" if ready == desired and desired > 0 else ("Degraded" if ready > 0 else "Failed")

                # Count restarts from pods
                restarts = 0
                try:
                    pods = self.core_v1.list_namespaced_pod(
                        namespace=self.namespace,
                        label_selector=f"{self.app_label}={app_name}"
                    )
                    for pod in pods.items:
                        for container in (pod.status.container_statuses or []):
                            restarts += container.restart_count or 0
                except Exception:
                    pass

                result[app_name] = {
                    "cluster": self.cluster_name,
                    "namespace": self.namespace,
                    "pods_ready": ready,
                    "pods_desired": desired,
                    "restarts": restarts,
                    "status": status,
                    "last_updated": dep.metadata.creation_timestamp.isoformat() if dep.metadata.creation_timestamp else None
                }
        except ApiException as e:
            logger.error(f"Error fetching deployments from {self.cluster_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error on {self.cluster_name}: {e}")

        return result
