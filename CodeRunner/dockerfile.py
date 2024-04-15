def generate_dockerfile(runtime_type):
    # Generate Dockerfile content based on runtime type
    # Example: for Python runtime
    dockerfile = ""
    if runtime_type == "python":
        dockerfile = f"""
        FROM python:3.9-slim
        WORKDIR /app
        COPY app.py /app/
        CMD ["python", "app.py"]
        """
    # Save the code to a file
    file_name = "Dockerfile"
    file_path = f"uploads/{file_name}"  # Example file path
    with open(file_path, "w") as file:
        file.write(dockerfile)
