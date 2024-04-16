from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort, inputs
import werkzeug.datastructures
from dockerfile import generate_dockerfile
from model import Image
from kube import KubeClient
import werkzeug
import json
import docker

app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Qube.sqlite3"
# initialize the app with the extension
api = Api(app)

docker_client = docker.client.from_env()

post_args = reqparse.RequestParser()
post_args.add_argument(
    "name", type=str, help="Provide job id", required=True, location="form"
)
post_args.add_argument(
    "type", type=str, help="Provide runtime type", required=True, location="form"
)
post_args.add_argument(
    "code", type=str, help="Provide runnable", required=True, location="form"
)
post_args.add_argument("command", type=str, location="form")
post_args.add_argument("dependency", type=inputs.boolean, location="form")
post_args.add_argument(
    "file", type=werkzeug.datastructures.FileStorage, location="files", action="append"
)

delete_args = reqparse.RequestParser()
delete_args.add_argument(
    "id", type=int, help="Provide id of function to delete", required=True
)
post_dispatch = reqparse.RequestParser()
post_dispatch.add_argument(
    "name", type=str, help="Provide function name to dispatch", required=True
)
post_dispatch.add_argument("type", type=str, help="Provide runtime type", required=True)

UNAME = "soumik13"
REPOSITORY = "soumik13/"
PAT = "dckr_pat_sR9jQhMqemR1JDxt13SvnCTZndU"
docker_client.login(UNAME, PAT)


class Register(Resource):
    def post(self):
        args = post_args.parse_args()
        code = args["code"]
        job_name = args["name"]
        runtime_type = args["type"]
        deps = args["dependency"]
        cmd = args["command"]
        tag = "function"
        image_name = f"{job_name}-{runtime_type}"
        # Get the files from the request
        files = args["file"]
        if files:
            # Process each file
            for file in files:
                # Save the file to a designated directory
                file.save("uploads/" + file.filename)

        # Save the code to a file
        file_name = "app.py"
        file_path = f"uploads/{file_name}"  # Example file path
        with open(file_path, "w") as file:
            file.write(code)

        generate_dockerfile(
            runtime_type,
            cmd.split() if cmd else None,
            True if deps else False,
        )

        # # Build Docker image
        built_image, json_logs = docker_client.images.build(
            path="uploads/",
            tag=f"{image_name}:{tag}",
        )
        built_image.tag(REPOSITORY + image_name, tag=tag)
        print(f"Pushing to image to registry {REPOSITORY + image_name}:{tag}")
        resp = docker_client.images.push(REPOSITORY + image_name, tag=tag)
        return "", 201

    def delete(self):
        return "", 204


class Dispatch(Resource):

    def post(self):
        args = post_dispatch.parse_args()
        job_name = args["name"]
        runtime_type = args["type"]
        kube = KubeClient()
        image = REPOSITORY + f"{job_name}-{runtime_type}" + ":function"

        kube.create_job(job_name, image)
        logs = kube.get_job_logs(job_name)
        logs = json.dumps({"logs": logs})
        print(logs)
        return "", 201


api.add_resource(Register, "/api/v1/register/")
api.add_resource(Dispatch, "/api/v1/dispatch/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8003)
