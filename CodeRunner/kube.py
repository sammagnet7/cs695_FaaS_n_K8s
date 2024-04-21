"""
Creates, Gets logs & status, and deletes a job object.
"""

from kubernetes import client, config, watch
import time
from time import sleep
import json


class KubeClient:
    def __init__(self) -> None:
        config.load_kube_config(
            "/home/arif/Kube/cs695/FAAS/cs695_FaaS_n_K8s/CodeRunner/config.yaml"
        )
        self.batch_api_instance = client.BatchV1Api()
        self.core_api_instance = client.CoreV1Api()
        self.job_object = None

    def create_namespace_safe(self, namespace):
        try:
            # Define the metadata for the namespace
            namespace_metadata = client.V1ObjectMeta(name=namespace)
            # Create an instance of the V1Namespace
            namespace = client.V1Namespace(
                kind="Namespace", metadata=namespace_metadata
            )
            # Create the namespace
            self.core_api_instance.create_namespace(namespace)

        except Exception as e:
            print(f"Namespace {namespace} exists")

    def __create_job_object(
        self, name: str, image: str, command=None, queue_name: str = ""
    ):
        # Configure Pod template container
        env_vars = [
            client.V1EnvVar(name="DB_NAME", value="s4_bucket"),
            client.V1EnvVar(name="DB_USER", value="cs695"),
            client.V1EnvVar(name="DB_PASSWORD", value="cs695"),
            client.V1EnvVar(name="DB_HOST", value="10.157.3.213"),
            client.V1EnvVar(name="DB_PORT", value="5432"),
            client.V1EnvVar(name="REDIS_HOST", value="10.157.3.213"),
            client.V1EnvVar(name="REDIS_PORT", value="6379"),
            client.V1EnvVar(name="QUEUE", value=queue_name),
            # Add more environment variables as needed
        ]
        container = client.V1Container(
            name=name,
            image=image,
            command=command,
            env=env_vars,
            resources=client.V1ResourceRequirements(
                limits={"cpu": "1.5", "memory": "512Mi"},  # limits for CPU and memory
                requests={
                    "cpu": "0.5",
                    "memory": "256Mi",
                },  # resource requests for CPU and memory
            ),
        )
        # Create and configure a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": name}),
            spec=client.V1PodSpec(restart_policy="Never", containers=[container]),
        )
        # Create the specification of deployment
        spec = client.V1JobSpec(
            template=template,
            backoff_limit=2,
            parallelism=1,
            ttl_seconds_after_finished=30,
        )
        # Instantiate the job object
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(name=name),
            spec=spec,
        )
        self.job_object = job

    def is_job_active(self, name: str, namespace: str = "default"):
        try:
            response = self.get_job_status(name, namespace=namespace)
            if response.active is None:  # job present but inactive
                return 1
            elif response.active > 0:  # job present and active
                return 2
            else:
                return 0  # fallback
        except Exception as e:
            if e.status == 404:  # job not found
                return 0

    def _create_job(
        self,
        name: str,
        image: str,
        command=None,
        namespace: str = "default",
        queue_name: str = "",
    ):
        self.__create_job_object(name, image, command, queue_name=queue_name)
        try:
            if namespace != "default":
                self.create_namespace_safe(namespace)
            api_response = self.batch_api_instance.create_namespaced_job(
                body=self.job_object, namespace=namespace
            )
            print(f"Job created in namespace'{namespace}'")
        except Exception as e:
            raise e

    def create_job_or_scale_existing(
        self,
        name: str,
        image: str,
        command=None,
        namespace: str = "default",
        queue_name: str = "s",
    ):
        status = self.is_job_active(name, namespace)
        match status:
            case 0:  # Create new job in the given namespace
                self._create_job(name, image, command, namespace, queue_name)
                return 0
            case 1:
                print(
                    f"Found inactive job in namespace {namespace}. Deleting and redeploying"
                )
                self.delete_job(name, namespace)
                self._create_job(name, image, command, namespace, queue_name)
                return 1
            case 2:
                print(f"Found active job in namespace {namespace}. Scaling it")
                self._scale_job_by(1, name, namespace)
                return 2

    def _scale_job_by(self, new_pod_count: int, name: str, namespace: str = "default"):
        try:
            job = self.batch_api_instance.read_namespaced_job(
                name=name, namespace=namespace
            )
            # print(job)
            # Update Job spec to increase the number of desired replicas/pods
            job.spec.parallelism += new_pod_count

            # Patch the Job to apply the updated spec
            self.batch_api_instance.patch_namespaced_job(
                name=name, namespace=namespace, body=job
            )
            print("Job scaled successfully!")
        except Exception as e:
            print(f"Error scaling the Job: {e}")

    def get_job_status(self, name, namespace="default"):
        try:
            api_response = self.batch_api_instance.read_namespaced_job_status(
                name=name, namespace=namespace, pretty=True
            )
            return api_response.status
        except Exception as e:
            raise e

    def _get_active_pod_count(self, name: str, namespace: str = "default"):
        try:
            api_response = self.batch_api_instance.read_namespaced_job_status(
                name=name, namespace=namespace, pretty=True
            )
            print(dict(api_response.status))
        except Exception as e:
            print("Error getting pod count")
            return -1

    def wait_for_pods_running(
        self, job_name, namespace="default", timeout=300, polling_interval=2
    ):
        start_time = time.time()
        while True:
            # Check if timeout has elapsed
            if time.time() - start_time > timeout:
                raise TimeoutError(
                    f"Timeout waiting for pods of Job to be in 'Running' state"
                )
            pods = self.core_api_instance.list_namespaced_pod(
                namespace=namespace, label_selector=f"job-name={job_name}"
            )
            # Check if all Pods are in 'Running' state
            all_good = all(pod.status.phase != "Pending" for pod in pods.items)
            if all_good:
                return

            # Sleep for polling interval before checking again
            time.sleep(polling_interval)

    def get_job_logs(self, job_name, namespace="default"):
        # Retrieve the list of Pods associated with the Job

        try:
            self.wait_for_pods_running(job_name=job_name)
            # Iterate over the Pods and fetch their logs
            pods = self.core_api_instance.list_namespaced_pod(
                namespace=namespace, label_selector=f"job-name={job_name}"
            )
            logs = []
            for pod in pods.items:
                pod_name = pod.metadata.name
                status = pod.status.phase
                try:
                    # Fetch logs for the Pod
                    pod_logs = self.core_api_instance.read_namespaced_pod_log(
                        name=pod_name,
                        namespace=namespace,
                        previous=False,
                        follow=False,
                        limit_bytes=10000000,
                    )
                    if status == "Failed":
                        message = pod.status.container_statuses[
                            0
                        ].state.terminated.message
                        reason = pod.status.container_statuses[
                            0
                        ].state.terminated.reason
                        logs.append(
                            f"Logs for Pod {pod_name}, status: {status}:\n{message}\nreason:{reason}"
                        )
                    else:
                        logs.append(
                            f"Logs for Pod {pod_name}, status: {status}:\n{pod_logs}"
                        )
                except Exception as e:
                    logs.append(f"Error fetching logs for Pod {pod_name}: {str(e)}")

            return logs
        except TimeoutError as e:
            return e

    def delete_job(self, job_name, namespace="default"):
        api_response = self.batch_api_instance.delete_namespaced_job(
            name=job_name,
            namespace=namespace,
            body=client.V1DeleteOptions(
                propagation_policy="Foreground", grace_period_seconds=5
            ),
        )
        print(f"Job deleted. status='{str(api_response.status)}'")


def main():
    name = "demo"
    image = "alpine"
    command = ["sleep", "120"]

    kube = KubeClient()
    # kube.create_job(name, image, command)
    # kube.scale_job_by(3, name)
    print(kube.get_job_status(name))


# if __name__ == "__main__":
#     main()
