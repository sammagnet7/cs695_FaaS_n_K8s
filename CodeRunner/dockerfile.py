images = {"python": "ubuntu:22.04"}


def generate_dockerfile(
    runtime_type, file_path, command=None, has_dependency: bool = False
):
    # Generate Dockerfile content based on runtime type
    # Example: for Python runtime
    dockerfile = ""
    if runtime_type == "python":
        dockerfile = f"""FROM {images.get(runtime_type)}
WORKDIR /app
ENV TZ=Asia/Calcutta
ENV LANG=en_US.UTF-8
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 python3 python3-pip -y
COPY ./ /app/
"""
        if has_dependency:
            dockerfile += (
                "RUN pip install -r requirements.txt\n"  # Install dependencies
            )
        if command:
            dockerfile += f"CMD {command}\n"
        else:
            dockerfile += "CMD python3 S4Service.py\n"
    # Save the code to a file
    file_name = "Dockerfile"
    with open(f"{file_path}/{file_name}", "w") as file:
        file.write(dockerfile)
