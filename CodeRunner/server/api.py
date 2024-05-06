from flask import Flask
from flask_restful import Api, Resource, reqparse
from server.dockerfile import generate_dockerfile
from server.kube import KubeClient

import docker
import os
import base64
import shutil

# TODO Abstract away DB stuff more
# TODO Publish a package to PyPI for S4Service and allow a simple api
# TODO Allow for simple functions to run (things like looping for each image shouldnt be implicit)
# TODO Ideally one trigger is one invocation of function

app = Flask(__name__)
# initialize the app with the extension
api = Api(app)

docker_client = docker.client.from_env()
# ----------------------------------------------------Function registration args --------------------------------------
post_args = reqparse.RequestParser()
post_args.add_argument("fnName", type=str, help="Provide job id", required=True)
post_args.add_argument("runtime", type=str, help="Provide runtime type", required=True)
post_args.add_argument("sourceCode", type=str, help="Provide runnable", required=True)
post_args.add_argument("command", type=str)
post_args.add_argument("requirements", type=str)
post_args.add_argument("replicaLimit", type=int)
post_args.add_argument("cpuMax", type=float)
post_args.add_argument("memoryMax", type=int)
# ---------------------------------------------------- Function dispatch args ----------------------------------------
post_dispatch = reqparse.RequestParser()
post_dispatch.add_argument(
    "fnName", type=str, help="Provide function name to dispatch", required=True
)
post_dispatch.add_argument(
    "runtime", type=str, help="Provide runtime type", required=True
)
post_dispatch.add_argument(
    "bucketName", type=str, help="Provide bucket id", required=True
)
# ----------------------------------------------------- Configs ----------------------------------------------------
REPOSITORY = "10.157.3.45:5000/"
UPLOADS_BASE = "uploads"
USERCODE = "app.py"
USERDEPS = "requirements.txt"
IMAGE_TAG = "function"
kube = KubeClient()  # kubernetes
script_directory = os.path.dirname(os.path.abspath(__file__))


def buildPath(path: str = ""):
    return os.path.abspath(os.path.join(script_directory, path))


# utils
def decodeB64(encodedstr):
    return base64.b64decode(encodedstr).decode()


def writeToFile(file_path, content: str = ""):
    with open(file_path, "w") as file:
        file.write(content)


def create_directory(directory_path):
    os.makedirs(directory_path, exist_ok=True)


def delete_directory(directory_path):
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)


class Register(Resource):
    def post(self):
        args = post_args.parse_args()
        # Required arguments
        code, job_name, runtime_type, instances, cpu, memory = (
            args["sourceCode"],
            args["fnName"],
            args["runtime"],
            args["replicaLimit"],
            args["cpuMax"],
            args["memoryMax"],
        )
        # optional arguments
        deps, cmd = args["requirements"], args["command"]
        image_name = f"{job_name}-{runtime_type}"
        try:
            # Create separate directory
            create_directory(buildPath(UPLOADS_BASE + f"/{job_name}"))
            # Copy scaffolding code
            shutil.copy(
                buildPath("../common/S4Service.py"),
                buildPath(f"{UPLOADS_BASE}/{job_name}/"),
            )
            # Save the user code to a file
            writeToFile(
                file_path=buildPath(f"{UPLOADS_BASE}/{job_name}/{USERCODE}"),
                content=decodeB64(code),
            )
            # Save dependencies if any
            if deps:
                writeToFile(
                    file_path=buildPath(f"{UPLOADS_BASE}/{job_name}/{USERDEPS}"),
                    content=decodeB64(deps),
                )
            generate_dockerfile(
                runtime_type,
                buildPath(f"{UPLOADS_BASE}/{job_name}"),
                cmd.split() if cmd else None,
                True if deps else False,
            )

            # # # Build Docker image
            built_image, json_logs = docker_client.images.build(
                path=buildPath(f"{UPLOADS_BASE}/{job_name}/"),
                tag=f"{image_name}:{IMAGE_TAG}",
            )
            built_image.tag(REPOSITORY + image_name, tag=IMAGE_TAG)
            print(f"Pushing to image to registry {REPOSITORY + image_name}:{IMAGE_TAG}")
            resp = docker_client.images.push(REPOSITORY + image_name, tag=IMAGE_TAG)

            kube.create_namespace_safe(job_name, cpu, memory, instances)
            return "Pushed image to remote successfully", 201

        except Exception as e:
            print(e)
            return "", 500
        finally:
            delete_directory(buildPath(f"{UPLOADS_BASE}/{job_name}/"))


class Dispatch(Resource):

    def post(self):
        try:
            args = post_dispatch.parse_args()
            job_name = args["fnName"]
            runtime_type = args["runtime"]
            bucket_id = args["bucketName"]
            image = REPOSITORY + f"{job_name}-{runtime_type}:" + f"{IMAGE_TAG}"
            queue_name = f"{job_name}_{bucket_id}_queue"
            if kube.namespace_exists(job_name):
                status = kube.create_job_or_scale_existing(
                    job_name, image, namespace=job_name, queue_name=queue_name
                )
                if status == 0:
                    return "Created Job", 201
                elif status == 1:
                    return "Created Job removing existing inactive Job", 201
                else:
                    return "Scaled existing job", 201
            else:
                return "Function not registered", 404
        except Exception as e:
            return "Something Went Wrong", 400


def get_summary_status(api_response):
    if (
        api_response.active is None
        and api_response.succeeded is not None
        and api_response.succeeded > 0
    ):  # Nothing active and atleast some success
        return {
            "status": "SUCCESS",
            "finishTime": api_response.completion_time.isoformat(),
        }
    elif (
        api_response.active is not None and api_response.active > 0
    ):  # Some pods still active
        return {"status": "PROCESSING"}
    elif (
        api_response.active is None
        and api_response.failed is not None
        and api_response.failed > 0
    ):  # Nothing active and all failed
        return {"status": "FAILED"}
    else:
        return {"status": "PROCESSING"}


class Status(Resource):

    def get(self, fnName):
        try:
            status = kube.get_job_status(fnName, fnName)
            status = get_summary_status(status)
            return status, 200
        except Exception as e:
            # print(e)
            return {"status": "Function couldn't be found"}, 200


from time import sleep
import threading
from threading import current_thread


class Test(Resource):
    def get(self):
        threadName = current_thread().name
        sleep(3)
        return f"Hello from thread : {threadName}", 200


create_directory(buildPath(UPLOADS_BASE))
api.add_resource(Test, "/api/v1/test")
api.add_resource(Register, "/api/v1/register")
api.add_resource(Dispatch, "/api/v1/dispatch")
api.add_resource(Status, "/api/v1/status/<string:fnName>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8003)
