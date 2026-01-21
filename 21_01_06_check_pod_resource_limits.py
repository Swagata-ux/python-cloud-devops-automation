"""
Docstring for 21_01_06_check_pod_resource_limits

Write a tool to check if all pods in a namespace are running with resource limits defined.

🎯 What this tool checks

For each Pod in a namespace, it verifies:
Every container has:
	•	resources.limits.cpu
	•	resources.limits.memory

If any container is missing limits, it reports it.

✅ Prerequisites

`pip install kubernetes`

Kubernetes access:
	•	Either ~/.kube/config
	•	Or running inside a cluster (ServiceAccount)

🧠 Design (Simple & Correct)
	•	Connect to Kubernetes API
	•	List Pods in a namespace
	•	Inspect each container's resource limits
	•	Report violations
	•	Exit with non-zero status if violations exist (CI/CD friendly)
"""

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
import sys
def load_kube_config():
    """
    Docstring for load_kube_config

    Load Kubernetes configuration.
    Works both locally and inside a cluster.
    """

    try:
        config.load_kube_config()
    except Exception:
        config.load_incluster_config()

def has_resources_limits(container) -> bool:
    resources = container.resources
    if not resources or not resources.limits:
        return False
    
    return "cpu" in resources.limits and "memory" in resources.limits
def check_namespace(namespace: str) -> bool:
    v1 = client.CoreV1Api()
    compliant = True

    try:
        pods = v1.list_namespaced_pod(namespace=namespace)
    except ApiException as e:
        print(f"Failed to list pods: {e}")
        sys.exit(1)
    
    for pod in pods.items:
        pod_name = pod.metadata.name
        for container in pod.spec.containers:
            if not has_resources_limits(container=container):
                compliant = False
                print(
                    f"❌ Pod: {pod_name}, Container: {container.name} "
                    f"→ Missing resource limits"
                    
                )
    return compliant
def main():
    if len(sys.argv) !=2:
        print("Usage: python check_pod_resource_limits.py <namespace>")
        sys.exit(1)

    namespace = sys.argv[1]
    load_kube_config()
    print(f"🔍 Checking resource limits in namespace: {namespace}")

    if check_namespace(namespace=namespace):
        print("✅ All pods have CPU and memory limits defined")
        sys.exit(0)
    else:
        print("❌ Some pods are missing resource limits")
        sys.exit(2)
if __name__ == "__main__":
    main()


   




    