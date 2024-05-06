import requests
import concurrent.futures
import time
import json
import requests

BASE = "http://localhost:8003/"
RAPI = "api/v1/register"
DAPI = "api/v1/dispatch"
SAPI = "api/v1/status/"
headers = {"Content-type": "application/json", "Accept": "*"}


def test_dispatch_helper(url, request_body):
    start_time = time.time()  # Capture start time
    response = requests.post(url, json=request_body, headers=headers)
    end_time = time.time()  # Capture end time
    return response.text, end_time - start_time  # Return response and time taken


def test_dispatch(url, request_body, count):
    # Send equests concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(test_dispatch_helper, url, request_body)
            for _ in range(count)
        ]

    # Get the results
    for future in concurrent.futures.as_completed(futures):
        response, time_taken = future.result()
        print("Response:", response)
        print("Time taken:", time_taken, "seconds")


def test_status(url):
    return requests.get(url)


def test_register(url, json):

    response = requests.post(url, json=json, headers=headers)
    return response


def load_json(path):
    request_body = None
    with open(path, "r") as file:
        request_body = json.load(file)
    return request_body


body = load_json("json/registerFn_log.json")
response = test_register(url=BASE + RAPI, json=body)
print(response.json())
test_dispatch(url=BASE + DAPI, request_body=body, count=1)
response = test_status(BASE + SAPI + "testlog")
print(response.json())
