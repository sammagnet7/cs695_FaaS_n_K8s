"""
Creates, scales, gets status, and deletes a job object.
"""

from kubernetes import client, config, watch
import threading
from threading import current_thread
import redis
import time
import math

job_locks = {}
REDIS_HOST = "10.157.3.213"
REDIS_PORT = "6379"
redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def get_current_redis_queue_size(queue_name: str):
    try:
        # Get the size of the queue
        queue_size = redis_conn.llen(queue_name)
        return queue_size
    except Exception as e:
        print(f"Error getting size of Redis queue {queue_name}: {e}")
        return None


class KubeClient:
    def __init__(self) -> None:
        config.load_kube_config(
            "/home/arif/Kube/cs695/FAAS/cs695_FaaS_n_K8s/CodeRunner/config.yaml"
        )
        self.batch_api_instance = client.BatchV1Api()
        self.core_api_instance = client.CoreV1Api()
        self.metric_api_instance = client.CustomObjectsApi()
        self.job_object = None
        self.max_instances = 16
        self.min_instances = 1
        self.max_cpu = 8
        self.min_cpu = 0.5
        self.max_mem = 4096
        self.min_mem = 256

    def scaler(self, jobname, queuename):
        workitems = get_current_redis_queue_size(queue_name=queuename)
        podcount = self._get_active_pod_count(jobname)
        print("Current pods: ", podcount)
        print("Current workitems: ", workitems)
        if workitems >= podcount * 20 or self.is_high_resource_usage(jobname):
            desired = workitems // 20
            amount = desired - podcount if podcount < desired else 0
            if amount > 0:
                print(f"Scaling to {desired} pods by adding {amount} pods")
                self._scale_job_by(amount, jobname, jobname)
            else:
                print(f"Not scaled, desired {desired} current {podcount}")
        else:
            print("Scale requirements not met")

    def is_high_resource_usage(self, namespace):
        THRESHOLD = 0.8
        pods = self.core_api_instance.list_namespaced_pod(namespace=namespace).items

        for pod in pods:
            pod_name = pod.metadata.name
            pod_namespace = pod.metadata.namespace
            containers = pod.spec.containers
            container_requests = {}

            for container in containers:
                requests = container.resources.requests
                cpu_request = requests.get("cpu", None)
                memory_request = requests.get("memory", None)
                print("cpu req", cpu_request)
                print("mem req", memory_request)
                container_requests = {
                    "cpu": int(cpu_request.rstrip("m")) if cpu_request else None,
                    "memory": (
                        int(memory_request.rstrip("Mi")) if memory_request else None
                    ),
                }
                print("container requests:", container_requests)

            # Get pod metrics
            cpu_usage, memory_usage = self.get_pod_resource_usage(
                pod_name, pod_namespace
            )
            if (
                cpu_usage / container_requests["cpu"] >= THRESHOLD
                or memory_usage / container_requests["memory"] >= THRESHOLD
            ):
                return True
        return False

    def get_pod_resource_usage(self, pod_name, namespace):
        group = "metrics.k8s.io"
        version = "v1beta1"
        plural = "pods"
        try:
            response = self.metric_api_instance.get_namespaced_custom_object(
                group, version, namespace, plural, pod_name
            )
            containers = response["containers"]
            cpu_usage = sum(
                [
                    int(container["usage"]["cpu"].rstrip("n")) / 1000000
                    for container in containers
                ]
            )
            memory_usage = sum(
                [
                    int(container["usage"]["memory"].rstrip("Ki")) / 1024
                    for container in containers
                ]
            )
            print(f"POD: {pod_name} cpu: {cpu_usage} mem:{memory_usage}")
            return cpu_usage, memory_usage
        except client.rest.ApiException as e:
            if e.status == 404:
                print("Pod not found or metrics not available.")
            else:
                print(f"Error: {e}")

        return 0, 0

    def read_metric(self, name, namespace):
        try:
            api = client.CustomObjectsApi()
            # k8s_nodes = api.list_cluster_custom_object(
            #     "metrics.k8s.io", "v1beta1", "pods"
            # )
            api.get_namespaced_custom_object(
                "metrics.k8s.io",
                "v1beta1",
            )
            # for stats in k8s_nodes["items"]:
            #     print(
            #         "Node Name: %s\tCPU: %s\tMemory: %s"
            #         % (
            #             stats["metadata"]["name"],
            #             stats["usage"]["cpu"],
            #             stats["usage"]["memory"],
            #         )
            #     )
        except Exception as e:
            print(
                "Exception when calling CoreV1Api->read_namespaced_resource_quota_status: %s\n"
                % e
            )

    def set_quotas_limits(self, ucpu, umemory, uinstances):
        resourceQuota = {"cpu": "0", "memory": "0", "instances": "0"}
        limitRange = {"cpu": "0", "memory": "0"}
        pcpu = pmem = pinstance = None
        # possible cpu
        if ucpu is None:
            pcpu = self.max_cpu
        elif ucpu is not None:
            pcpu = ucpu if ucpu <= self.max_cpu else self.max_cpu
        # possible memory
        if umemory is not None:
            if umemory >= self.min_mem and umemory <= self.max_mem:
                pmem = umemory
            else:
                pmem = self.max_mem
        elif umemory is None:
            pmem = self.max_mem
        # possible instance
        if uinstances is None or uinstances > self.max_instances:
            pinstance = self.max_instances
        elif uinstances is not None and uinstances < self.max_instances:
            pinstance = uinstances

        # quotas and limits
        resourceQuota["cpu"] = pcpu
        limitRange["cpu"] = (
            self.min_cpu
            if resourceQuota["cpu"] / pinstance <= self.min_cpu
            else resourceQuota["cpu"] / pinstance
        )
        resourceQuota["memory"] = pmem
        limitRange["memory"] = (
            self.min_mem
            if resourceQuota["memory"] / pinstance <= self.min_mem
            else resourceQuota["memory"] / pinstance
        )
        resourceQuota["instances"] = pinstance
        return resourceQuota, limitRange

    def create_namespace_safe(self, name, cpu, memory, instance):
        while True:
            try:
                # Define the metadata for the namespace
                namespace_metadata = client.V1ObjectMeta(name=name)
                # Create an instance of the V1Namespace
                _namespace = client.V1Namespace(
                    kind="Namespace", metadata=namespace_metadata
                )
                # Create the namespace
                self.core_api_instance.create_namespace(_namespace)
                break
            except client.ApiException as e:
                if e.status == 409:  # Namespace already exists
                    print(f"Namespace {name} exists, Deleting...")
                    try:
                        self.core_api_instance.delete_namespace(name=name)
                    except client.ApiException as delete_exception:
                        if delete_exception.status == 404:  # Namespace not found
                            continue  # Namespace is already deleted, break the loop
                        else:
                            print(
                                f"Failed to delete namespace {name}: {delete_exception}"
                            )
                else:
                    print(f"Failed to create namespace {name}: {e}")
                    break
        print("Applying quotas")
        resourceQuota, limitRange = self.set_quotas_limits(cpu, memory, instance)
        print("Resource quota:", resourceQuota)
        print("Limit range:", limitRange)
        self.create_resource_quota(
            name,
            cpu=resourceQuota["cpu"],
            memory=resourceQuota["memory"],
            instance=resourceQuota["instances"],
        )
        self.create_limit_range(
            name,
            cpu=limitRange["cpu"],
            memory=limitRange["memory"],
            maxcpu=resourceQuota["cpu"],
            maxmem=resourceQuota["memory"],
        )

    def create_resource_quota(self, namespace, cpu, memory, instance):
        try:
            quota = client.V1ResourceQuota(
                metadata=client.V1ObjectMeta(name="cpu-mem-rq"),
                spec=client.V1ResourceQuotaSpec(
                    hard={
                        "pods": str(instance),
                        "requests.cpu": str(cpu),
                        "requests.memory": str(memory) + "Mi",
                        "limits.cpu": str(cpu),
                        "limits.memory": str(memory) + "Mi",
                    }
                ),
            )
            self.core_api_instance.create_namespaced_resource_quota(
                namespace=namespace, body=quota
            )

        except Exception as e:
            print("Failed to create resource quota ", e)

    def create_limit_range(self, namespace, cpu, memory, maxcpu, maxmem):
        print("limit range got mem:", memory)
        try:
            limit_range = client.V1LimitRange(
                metadata=client.V1ObjectMeta(name="cpu-mem-lr"),
                spec=client.V1LimitRangeSpec(
                    limits=[
                        client.V1LimitRangeItem(
                            min={
                                "cpu": str(cpu),
                                "memory": str(math.floor(memory)) + "Mi",
                            },
                            max={
                                "cpu": str(maxcpu),
                                "memory": str(math.floor(maxmem)) + "Mi",
                            },
                            default_request={
                                "cpu": str(cpu),
                                "memory": str(math.floor(memory)) + "Mi",
                            },
                            default={
                                "cpu": str(cpu),
                                "memory": str(math.floor(memory)) + "Mi",
                            },
                            type="Container",
                        )
                    ]
                ),
            )
            self.core_api_instance.create_namespaced_limit_range(
                namespace=namespace, body=limit_range
            )

        except Exception as e:
            print("Failed to create limit range ", e)

    def __create_job_object(
        self,
        name: str,
        image: str,
        command=None,
        queue_name: str = "",
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
        )
        # Create and configure a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": name}),
            spec=client.V1PodSpec(restart_policy="Never", containers=[container]),
        )
        # Create the specification of deployment
        spec = client.V1JobSpec(
            template=template,
            backoff_limit=1,
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
            if (
                response.start_time != None and response.active is None
            ):  # job present but inactive
                return 1
            elif response.start_time is None and response.active is None:
                return 2
            elif response.active > 0:  # job present and active
                return 2
            else:
                return 0  # fallback
        except Exception as e:
            # print("is job active")
            # print(e)
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
        while 1:
            try:
                api_response = self.batch_api_instance.create_namespaced_job(
                    body=self.job_object, namespace=namespace
                )
                print(f"Job created in namespace'{namespace}'")
                break
            except Exception as e:
                print("KUBE Job:", e)
                print("Trying again")

    def create_job_or_scale_existing(
        self,
        name: str,
        image: str,
        command=None,
        namespace: str = "default",
        queue_name: str = "",
    ):
        lock = job_locks.setdefault(name, threading.Lock())
        lock.acquire()
        status = self.is_job_active(name, namespace)
        match status:
            case 0:  # Create new job in the given namespace
                print("Creating job normally")
                self._create_job(name, image, command, namespace, queue_name)
                self.scaler(jobname=name, queuename=queue_name)
                lock.release()
                return 0
            case 1:
                print(
                    f"Found inactive job in namespace {namespace}. Deleting and redeploying"
                )
                self.delete_job(name, namespace)
                self._create_job(name, image, command, namespace, queue_name)
                lock.release()
                return 1
            case 2:
                # print(f"Found active job in namespace {namespace}.trying to scale it")
                print(f"Found active job in namespace {namespace}.Ignoring")
                self.scaler(jobname=name, queuename=queue_name)
                lock.release()
                return 2

    def _scale_job_by(self, new_pod_count: int, name: str, namespace: str = "default"):
        while 1:
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
                break
            except Exception as e:

                if e.reason == "Conflict":
                    print(f"Error scaling the Job")
                else:
                    print("SCALE Exception:", e)

    def get_job_status(self, name, namespace="default"):
        try:
            api_response = self.batch_api_instance.read_namespaced_job_status(
                name=name, namespace=namespace, pretty=True
            )
            return api_response.status
        except Exception as e:
            # print("exception in status", e)
            raise e

    def _get_active_pod_count(self, namespace: str = "default"):
        try:
            pods = self.core_api_instance.list_namespaced_pod(namespace=namespace).items
            active_count = 0
            for pod in pods:
                if pod.status.phase in ["Running", "Pending"]:
                    active_count += 1
            print(f"Namespace {namespace} active pods: {active_count}")
            return active_count
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
    kube._get_active_pod_count("kube-system")
    test_cases = [
        (None, None, None),
        (0.5, 512, None),
        (None, 1024, 2),
        (0.7, None, 5),
        # (400, 2048, 1),
        # (100, 256, 4),
    ]

    max_cpu = 8
    max_mem = 4096
    max_instances = 16
    min_cpu = 0.5
    min_mem = 256
    min_instances = 1
    # for cpu in [i / 2 for i in range(0, 25)]:
    #     for mem in range(128, 1024 * 5, 128):
    #         for instances in range(0, 18, 1):
    #             test_cases.append((cpu, mem, instances))

    # for cpu, memory, instances in test_cases:
    #     print(f"Input: cpu={cpu}, memory={memory}, instances={instances}")
    #     validated_cpu, validated_memory, validated_instances = kube.validate_resources(
    #         cpu, memory, instances
    #     )
    #     print(
    #         f"Output: cpu={validated_cpu}, memory={validated_memory}, instances={validated_instances}"
    #     )
    # print("-" * 30)


# if __name__ == "__main__":
#     main()
