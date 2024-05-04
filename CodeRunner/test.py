import requests
import concurrent.futures
import time

json = {"fnName": "testmatrix", "runtime": "python", "bucketId": "testmatrix"}


def send_request():
    start_time = time.time()  # Capture start time
    response = requests.post("http://localhost:8003/api/v1/dispatch", json=json)
    end_time = time.time()  # Capture end time
    return response.text, end_time - start_time  # Return response and time taken


# Send 5 requests concurrently
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(send_request) for _ in range(500)]

# Get the results
for future in concurrent.futures.as_completed(futures):
    response, time_taken = future.result()
    print("Response:", response)
    print("Time taken:", time_taken, "seconds")
