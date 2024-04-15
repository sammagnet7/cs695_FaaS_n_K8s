"""
Creates, Gets logs & status, and deletes a job object.
"""

from kubernetes import client, config
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

    def __create_job_object(self, name: str, image: str, command: list):
        # Configure Pod template container
        container = client.V1Container(
            name=name,
            image=image,
            command=command,
            resources=client.V1ResourceRequirements(
                limits={"cpu": "0.5", "memory": "512Mi"},  # limits for CPU and memory
                requests={
                    "cpu": "0.1",
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
        spec = client.V1JobSpec(template=template, backoff_limit=4)
        # Instantiate the job object
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(name=name),
            spec=spec,
        )
        self.job_object = job

    def create_job(
        self, name: str, image: str, command: list, namespace: str = "default"
    ):
        self.__create_job_object(name, image, command)
        api_response = self.batch_api_instance.create_namespaced_job(
            body=self.job_object, namespace=namespace
        )
        print(f"Job created. status='{str(api_response.status)}'")

    def get_job_status(self, name, namespace="default"):
        job_completed = False
        while not job_completed:
            api_response = self.batch_api_instance.read_namespaced_job_status(
                name=name, namespace=namespace, pretty=True
            )
            if (
                api_response.status.succeeded is not None
                or api_response.status.failed is not None
            ):
                job_completed = True
            return api_response.status

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
                print(pod)
                pod_name = pod.metadata.name
                status = pod.status.phase
                try:
                    # Fetch logs for the Pod
                    pod_logs = self.core_api_instance.read_namespaced_pod_log(
                        name=pod_name, namespace=namespace
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
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    name = "pi"
    image = "perl"  # Example image for Perl
    command = [
        "perl",
        "-Mbignum=bpi",
        "-wle",
        "print bpi(200)",
    ]  # Example command for printing digits of pi in Perl
    kube = KubeClient()
    kube.create_job(name, image, command)
    logs = kube.get_job_logs(name)
    logs = json.dumps({"logs": logs})
    print(logs)
    # kube.delete_job(name)

    # Create a job object with client-python API. The job we
    # created is same as the `pi-job.yaml` in the /examples folder.
    # job = create_job_object(name, image, command)

    # create_job(batch_v1, job)

    # get_job_status(name, batch_v1)
    # # update_job(batch_v1, job)

    # delete_job(name, batch_v1)


if __name__ == "__main__":
    main()
