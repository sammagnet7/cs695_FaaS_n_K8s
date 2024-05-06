#!/bin/bash

# Ensure cluster is setup before doing following

# 1. Running flask backend
echo "Running flask backend..."
python3 -m venv env
source ./env/bin/activate
pip install -r ./CodeRunner/requirements.txt
cd CodeRunner/ || exit
python3 run.py &
cd ..

# 2. Running middleware: Start the Spring boot APIs: faas and s4bucket
echo "Running middleware..."

# First cd to base directory i.e. cs695_FaaS_n_K8s
cd Middleware/RegistryService || exit
echo "Building and running RegistryService..."
./mvnw clean package
java -jar target/RegistryService-0.0.1-SNAPSHOT.jar &
cd ../S4BucketService || exit
echo "Building and running S4BucketService..."
./mvnw clean package
java -jar target/S4BucketService-0.0.1-SNAPSHOT.jar &
cd ../../

# 3. Running frontend
echo "Running frontend..."
cd Frontend/faas-frontend || exit
echo "Installing dependencies..."
npm install
echo "Starting npm run dev..."
npm run dev
