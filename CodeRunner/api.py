from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort, inputs
import werkzeug.datastructures
from dockerfile import generate_dockerfile
from kube import KubeClient
import werkzeug
import redis
import docker
import os
import base64
import shutil

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
# ---------------------------------------------------- Function dispatch args ----------------------------------------
post_dispatch = reqparse.RequestParser()
post_dispatch.add_argument(
    "fnName", type=str, help="Provide function name to dispatch", required=True
)
post_dispatch.add_argument(
    "runtime", type=str, help="Provide runtime type", required=True
)
post_dispatch.add_argument(
    "bucketId", type=str, help="Provide bucket id", required=True
)
# ----------------------------------------------------- Configs ----------------------------------------------------
UNAME = "soumik13"
REPOSITORY = "soumik13/"
REDIS_HOST = "10.157.3.213"
REDIS_PORT = "6379"
PAT = "dckr_pat_sR9jQhMqemR1JDxt13SvnCTZndU"
docker_client.login(UNAME, PAT)  # docket
kube = KubeClient()  # kubernetes
redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def decodeB64(encodedstr):
    return base64.b64decode(encodedstr).decode()


def get_current_redis_queue_size(queue_name: str):
    try:
        # Get the size of the queue
        queue_size = redis_conn.llen(queue_name)
        return queue_size
    except Exception as e:
        print(f"Error getting size of Redis queue {queue_name}: {e}")
        return None


class Register(Resource):
    def post(self):
        args = post_args.parse_args()
        # Required arguments
        code = args["sourceCode"]
        job_name = args["fnName"]
        runtime_type = args["runtime"]
        # optional arguments
        deps = args["requirements"]
        cmd = args["command"]
        tag = "function"
        image_name = f"{job_name}-{runtime_type}"
        # Create separate directory
        os.makedirs(os.path.join("./uploads/", f"{job_name}"))
        # Copy scaffolding code
        shutil.copy("./uploads/common/S4Service.py", f"./uploads/{job_name}/")
        # Save the user code to a file
        code = decodeB64(code)
        file_name = "app.py"
        file_path = f"uploads/{job_name}/{file_name}"  # Example file path
        with open(file_path, "w") as file:
            file.write(code)
        if deps:
            deps = decodeB64(deps)
            file_name = "requirements.txt"
            file_path = f"uploads/{job_name}/{file_name}"
            with open(file_path, "w") as file:
                file.write(deps)

        generate_dockerfile(
            runtime_type,
            f"uploads/{job_name}",
            cmd.split() if cmd else None,
            True if deps else False,
        )

        # # # Build Docker image
        built_image, json_logs = docker_client.images.build(
            path=f"uploads/{job_name}/",
            tag=f"{image_name}:{tag}",
        )
        built_image.tag(REPOSITORY + image_name, tag=tag)
        print(f"Pushing to image to registry {REPOSITORY + image_name}:{tag}")
        resp = docker_client.images.push(REPOSITORY + image_name, tag=tag)
        shutil.rmtree(f"uploads/{job_name}")
        return "Pushed image to remote successfully", 201

    def delete(self):
        return "", 204


class Dispatch(Resource):

    def post(self):
        try:
            args = post_dispatch.parse_args()
            job_name = args["fnName"]
            runtime_type = args["runtime"]
            bucket_id = args["bucketId"]

            print(job_name)
            print(runtime_type)
            print(bucket_id)

            image = REPOSITORY + f"{job_name}-{runtime_type}" + ":function"
            queue_name = f"{job_name}_{bucket_id}_queue"

            status = kube.create_job_or_scale_existing(
                job_name, image, namespace=job_name, queue_name=queue_name
            )

            print(get_current_redis_queue_size(queue_name))
            if status == 0:
                return "Created Job", 201
            elif status == 1:
                return "Created Job removing existing inactive Job", 201
            else:
                return "Scaled existing job", 201
        except Exception as e:
            print(e)
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
            return "Function couldn't be found", 200


api.add_resource(Register, "/api/v1/register")
api.add_resource(Dispatch, "/api/v1/dispatch")
api.add_resource(Status, "/api/v1/status/<string:fnName>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8003)
