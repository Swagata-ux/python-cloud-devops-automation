"""
EC2 Idle Instance Detector
Detects and safely terminates idle EC2 instances based on CPU utilization.

Requirements:
- pip install boto3
- AWS credentials configured
- IAM permissions:
  ec2:DescribeInstances
  ec2:TerminateInstances
  cloudwatch:GetMetricStatistics
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import logging
import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class EC2IdleDetector:
    def __init__(
        self,
        region: str = "us-east-1",
        cpu_threshold: float = 5.0,
        idle_hours: int = 24,
        protected_tags: List[str] | None = None,
    ):
        if not region.strip():
            raise ValueError("Region must be a non-empty string")
        if cpu_threshold < 0:
            raise ValueError("cpu_threshold must be >= 0")
        if idle_hours < 0:
            raise ValueError("idle_hours must be >= 0")

        self.region = region
        self.cpu_threshold = cpu_threshold
        self.idle_hours = idle_hours
        self.protected_tags = [t.lower() for t in (protected_tags or ["production", "critical", "database"])]

        self.ec2 = boto3.client("ec2", region_name=region)
        self.cloudwatch = boto3.client("cloudwatch", region_name=region)

        logging.info(f"AWS clients initialized for region {region}")

    # -----------------------------
    # EC2 INSTANCE DISCOVERY
    # -----------------------------
    def get_running_instances(self) -> List[Dict[str, Any]]:
        try:
            paginator = self.ec2.get_paginator("describe_instances")
            instances = []

            for page in paginator.paginate(
                Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
            ):
                for reservation in page.get("Reservations", []):
                    instances.extend(reservation.get("Instances", []))

            logging.info(f"Found {len(instances)} running instances")
            return instances

        except ClientError as e:
            logging.error(f"Failed to describe instances: {e}")
            return []

    # -----------------------------
    # CPU UTILIZATION
    # -----------------------------
    def get_cpu_utilization(self, instance_id: str) -> float:
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=self.idle_hours)

        try:
            response = self.cloudwatch.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName="CPUUtilization",
                Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=["Average"],
            )

            datapoints = response.get("Datapoints", [])
            if not datapoints:
                return 0.0

            avg_cpu = sum(dp["Average"] for dp in datapoints) / len(datapoints)
            return round(avg_cpu, 2)

        except ClientError as e:
            logging.error(f"CloudWatch error for {instance_id}: {e}")
            return 0.0

    # -----------------------------
    # PROTECTION CHECK
    # -----------------------------
    def is_protected(self, instance: Dict[str, Any]) -> bool:
        for tag in instance.get("Tags", []):
            if tag.get("Value", "").lower() in self.protected_tags:
                return True
        return False

    # -----------------------------
    # IDLE DETECTION
    # -----------------------------
    def detect_idle_instances(self) -> List[str]:
        idle_instances = []
        now = datetime.now(timezone.utc)

        for instance in self.get_running_instances():
            instance_id = instance.get("InstanceId")
            launch_time = instance.get("LaunchTime")

            if not instance_id or not launch_time:
                continue

            if self.is_protected(instance):
                logging.info(f"{instance_id} is protected")
                continue

            uptime_hours = (now - launch_time).total_seconds() / 3600
            if uptime_hours < self.idle_hours:
                continue

            cpu_avg = self.get_cpu_utilization(instance_id)
            logging.info(f"{instance_id}: CPU={cpu_avg}%, uptime={uptime_hours:.1f}h")

            if cpu_avg < self.cpu_threshold:
                idle_instances.append(instance_id)
                logging.warning(f"Idle instance detected: {instance_id}")

        return idle_instances

    # -----------------------------
    # TERMINATION
    # -----------------------------
    def terminate_instances(self, instance_ids: List[str], dry_run: bool = True) -> Dict[str, List[str]]:
        if dry_run:
            logging.info(f"[DRY RUN] Would terminate: {instance_ids}")
            return {"terminated": instance_ids, "failed": []}

        terminated, failed = [], []

        for instance_id in instance_ids:
            try:
                self.ec2.terminate_instances(InstanceIds=[instance_id])
                terminated.append(instance_id)
                logging.info(f"Termination initiated for {instance_id}")

            except ClientError as e:
                logging.error(f"Failed to terminate {instance_id}: {e}")
                failed.append(instance_id)

        return {"terminated": terminated, "failed": failed}


# -----------------------------
# MAIN
# -----------------------------
def main(region: str, cpu_threshold: float, idle_hours: int, dry_run: bool):
    detector = EC2IdleDetector(
        region=region,
        cpu_threshold=cpu_threshold,
        idle_hours=idle_hours,
    )

    idle_instances = detector.detect_idle_instances()

    if not idle_instances:
        logging.info("No idle instances found")
        return

    result = detector.terminate_instances(idle_instances, dry_run=dry_run)

    logging.info(f"Summary: {len(result['terminated'])} terminated, {len(result['failed'])} failed")


if __name__ == "__main__":
    import argparse
    import time

    parser = argparse.ArgumentParser(description="Detect and terminate idle EC2 instances")
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--cpu-threshold", type=float, default=5.0)
    parser.add_argument("--idle-hours", type=int, default=24)
    parser.add_argument("--execute", action="store_true", help="Actually terminate instances")

    args = parser.parse_args()
    dry_run = not args.execute

    if dry_run:
        logging.info("Running in DRY-RUN mode")
    else:
        logging.warning("EXECUTION MODE ENABLED — instances will be terminated")
        time.sleep(3)

    main(
        region=args.region,
        cpu_threshold=args.cpu_threshold,
        idle_hours=args.idle_hours,
        dry_run=dry_run,
    )
