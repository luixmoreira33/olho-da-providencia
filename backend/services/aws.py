import boto3
import logging
from typing import Dict, List, Optional
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)


class AWSClient:
    def __init__(self, region: str, access_key: Optional[str] = None, secret_key: Optional[str] = None):
        self.region = region
        self.configured = False
        self.ec2 = None
        self.ecs = None

        try:
            session_kwargs = {"region_name": region}
            if access_key and secret_key:
                session_kwargs["aws_access_key_id"] = access_key
                session_kwargs["aws_secret_access_key"] = secret_key

            session = boto3.Session(**session_kwargs)
            self.ec2 = session.client("ec2")
            self.ecs = session.client("ecs")
            # Quick test
            self.ec2.describe_instances(MaxResults=5)
            self.configured = True
            logger.info(f"AWS client configured for region {region}")
        except NoCredentialsError:
            logger.warning("AWS credentials not found")
        except Exception as e:
            logger.warning(f"Failed to configure AWS client: {e}")

    def get_ec2_status(self) -> Dict[str, dict]:
        if not self.configured:
            return {}

        result = {}
        try:
            paginator = self.ec2.get_paginator("describe_instances")
            for page in paginator.paginate():
                for reservation in page.get("Reservations", []):
                    for instance in reservation.get("Instances", []):
                        name = next(
                            (t["Value"] for t in instance.get("Tags", []) if t["Key"] == "Name"),
                            instance["InstanceId"]
                        )
                        state = instance["State"]["Name"]
                        status = "Healthy" if state == "running" else ("Warning" if state in ("pending", "stopping") else "Critical")

                        result[name] = {
                            "type": "ec2",
                            "id": instance["InstanceId"],
                            "state": state,
                            "status": status,
                            "instance_type": instance.get("InstanceType"),
                            "private_ip": instance.get("PrivateIpAddress"),
                        }
        except Exception as e:
            logger.error(f"Error fetching EC2 instances: {e}")

        return result

    def get_ecs_status(self) -> Dict[str, dict]:
        if not self.configured:
            return {}

        result = {}
        try:
            clusters = self.ecs.list_clusters().get("clusterArns", [])
            for cluster_arn in clusters:
                cluster_name = cluster_arn.split("/")[-1]
                services = self.ecs.list_services(cluster=cluster_arn).get("serviceArns", [])

                if not services:
                    continue

                desc = self.ecs.describe_services(cluster=cluster_arn, services=services)
                for svc in desc.get("services", []):
                    name = f"{cluster_name}/{svc['serviceName']}"
                    running = svc.get("runningCount", 0)
                    desired = svc.get("desiredCount", 0)
                    status = "Healthy" if running == desired and desired > 0 else ("Warning" if running > 0 else "Critical")

                    result[name] = {
                        "type": "ecs",
                        "cluster": cluster_name,
                        "service": svc["serviceName"],
                        "running": running,
                        "desired": desired,
                        "status": status,
                    }
        except Exception as e:
            logger.error(f"Error fetching ECS services: {e}")

        return result
