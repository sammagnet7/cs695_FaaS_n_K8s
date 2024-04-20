images = {"python": "python:slim"}


def generate_dockerfile(runtime_type, command=None, has_dependency: bool = False):
    # Generate Dockerfile content based on runtime type
    # Example: for Python runtime
    dockerfile = ""
    if runtime_type == "python":
        dockerfile = f"""
        FROM {images.get(runtime_type)}
        WORKDIR /app
        COPY ./ /app/
        """
        if has_dependency:
            dockerfile += (
                "RUN pip install -r requirements.txt\n"  # Install dependencies
            )
        if command:
            dockerfile += f"CMD {command}\n"
        else:
            dockerfile += 'CMD ["python", "app.py"]\n'
    # Save the code to a file
    file_name = "Dockerfile"
    file_path = f"uploads/{file_name}"  # Example file path
    with open(file_path, "w") as file:
        file.write(dockerfile)
