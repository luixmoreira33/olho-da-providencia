"""Resilient AWS connector (EC2 + ECS)."""
from typing import Dict, Optional
import boto3
import logging
from botocore.exceptions import ClientError, NoCredentialsError

from services.base import BaseConnector

logger = logging.getLogger(__name__)


class AWSConnector(BaseConnector):
    def __init__(self, region: str, access_key: Optional[str] = None, secret_key: Optional[str] = None):
        super().__init__("aws", timeout=20)
        self.region = region
        self.ec2 = None
        self.ecs = None

        try:
            kwargs = {"region_name": region}
            if access_key and secret_key:
                kwargs["aws_access_key_id"] = access_key
                kwargs["aws_secret_access_key"] = secret_key
            session = boto3.Session(**kwargs)
            self.ec2 = session.client("ec2")
            self.ecs = session.client("ecs")
            self.ec2.describe_instances(MaxResults=5)
            self.configured = True
            logger.info("AWS connector ready")
        except Exception as e:
            logger.warning(f"AWS not configured: {e}")

    def _fetch(self) -> Dict:
        if not self.ec2 or not self.ecs:
            raise RuntimeError("AWS clients not initialized")

        result = {"ec2": {}, "ecs": {}}

        # EC2
        paginator = self.ec2.get_paginator("describe_instances")
        for page in paginator.paginate():
            for res in page.get("Reservations", []):
                for inst in res.get("Instances", []):
                    name = next((t["Value"] for t in inst.get("Tags", []) if t["Key"] == "Name"), inst["InstanceId"])
                    state = inst["State"]["Name"]
                    status = "Healthy" if state == "running" else ("Warning" if state in ("pending", "stopping") else "Critical")
                    result["ec2"][name] = {
                        "id": inst["InstanceId"],
                        "state": state,
                        "status": status,
                        "type": inst.get("InstanceType"),
                    }

        # ECS
        clusters = self.ecs.list_clusters().get("clusterArns", [])
        for arn in clusters:
            cname = arn.split("/")[-1]
            services = self.ecs.list_services(cluster=arn).get("serviceArns", [])
            if not services:
                continue
            desc = self.ecs.describe_services(cluster=arn, services=services)
            for svc in desc.get("services", []):
                key = f"{cname}/{svc['serviceName']}"
                running = svc.get("runningCount", 0)
                desired = svc.get("desiredCount", 0)
                status = "Healthy" if running == desired and desired > 0 else ("Warning" if running > 0 else "Critical")
                result["ecs"][key] = {
                    "cluster": cname,
                    "service": svc["serviceName"],
                    "running": running,
                    "desired": desired,
                    "status": status,
                }

        return result
