
cd /Users/soumikdutta/LocalDrive/Mtech_2026/IITB/Docs/Academics/IITNotes/Class_notes/sem_2/CS695_VCC/Assignments/Assignment4/Workspace/cs695_FaaS_n_K8s
python3 -m venv env

source ./env/bin/activate

pip install -r ./CodeRunner/requirements.txt

In the host system where we are running the Flask applicatiion, modify below setup in the Docker engine configuration:
"insecure-registries": [
    "10.157.3.45:5000"
  ]

1.
cd CodeRunner
python3 run.py

2. 
cd RegistryService/Frontend/faas-frontend
npm run dev
Open URL: http://localhost:5173/

3.
Start the Spring boot APIs: faas and s4bucket

4. Running middleware:
# First cd to base directory i.e. cs695_FaaS_n_K8s then,
    cd Middleware/RegistryService
    ./mvnw clean package
    java -jar target/RegistryService-0.0.1-SNAPSHOT.jar
# Second cd to base directory i.e. cs695_FaaS_n_K8s then,
    cd Middleware/S4BucketService
    ./mvnw clean package
    java -jar target/S4BucketService-0.0.1-SNAPSHOT.jar

