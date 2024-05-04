import os
import csv
import requests
import time
import matplotlib.pyplot as plt

COMMON_VALUES = {
    "runtime": "python",
    "entryFn": "userDefinedFunction",
    "triggerType": "CLOUD_STORAGE",
    "eventType": "UPLOAD_INTO_BUCKET",
    "replicaLimit": "1",
    "cpuMax": "4",
    "memoryMax": "2048",
    "resourceFolderPath":"src/main/resources"
}

def get_testlog_data():
    data =  {
        "fnName": "testlog",
        "bucketName": "testlog",
        "sourceCode": "IyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMKIyBBZGQgeW91ciBpbXBvcnRzIGhlcmUKIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMKIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIwojIEVudGVyIHlvdSBCdWNrZXQgbmFtZSBoZXJlCiMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMKQlVDS0VUX05BTUUgPSAidGVzdGxvZyIKCiMgRG8gbm90IGVkaXQgdGhpcyBmdW5jdGlvbiBuYW1lCmRlZiB1c2VyRGVmaW5lZEZ1bmN0aW9uKGltYWdlX29sZCk6ICAjIFRoaXMgaXMgYSBCYXNlNjY0IGVuY29kZWQgc3RyaW5nCiAgICBpbWFnZV9uZXcgPSAiIgogICAgcHJpbnQoIkxPRzogSHdsbG8gQ1M2OTUiKQogICAgcmV0dXJuIGltYWdlX25ldwo=",
        "requirements": "cmVkaXMKcHN5Y29wZzI="
    }
    data.update(COMMON_VALUES)
    return data


def get_testgray_data():
    data= {
        "fnName": "testgray",
        "bucketName": "testgray",
        "sourceCode": "IyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMKIyBBZGQgeW91ciBpbXBvcnRzIGhlcmUKIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMKZnJvbSBQSUwgaW1wb3J0IEltYWdlLCBJbWFnZU9wcwppbXBvcnQgYmFzZTY0CmltcG9ydCBpbwppbXBvcnQgdGltZQoKCiMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMKIyBFbnRlciB5b3UgQnVja2V0IG5hbWUgaGVyZQojIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjCkJVQ0tFVF9OQU1FID0gInRlc3RncmF5IgoKIyBEbyBub3QgZWRpdCB0aGlzIGZ1bmN0aW9uIG5hbWUKZGVmIHJlYWRfYmFzZTY0X2ltYWdlKGJhc2U2NF9zdHJpbmcpOgogICAgaW1hZ2VfZGF0YSA9IGJhc2U2NC5iNjRkZWNvZGUoYmFzZTY0X3N0cmluZykKICAgIGltYWdlX3N0cmVhbSA9IGlvLkJ5dGVzSU8oaW1hZ2VfZGF0YSkKCiAgICByZXR1cm4gaW1hZ2Vfc3RyZWFtCgoKZGVmIGVuY29kZV9iYXNlNjRfaW1hZ2UoaW1hZ2UpOgogICAgaW1hZ2Vfc3RyZWFtID0gaW8uQnl0ZXNJTygpCiAgICBpbWFnZS5zYXZlKGltYWdlX3N0cmVhbSwgZm9ybWF0PSJQTkciKQogICAgX2ltYWdlX2J5dGVzID0gaW1hZ2Vfc3RyZWFtLmdldHZhbHVlKCkKICAgIGJhc2U2NF9zdHJpbmcgPSBiYXNlNjQuYjY0ZW5jb2RlKF9pbWFnZV9ieXRlcykuZGVjb2RlKCJ1dGYtOCIpCiAgICByZXR1cm4gYmFzZTY0X3N0cmluZwoKCmRlZiB1c2VyRGVmaW5lZEZ1bmN0aW9uKGltYWdlX29sZCk6CiAgICBzdGFydF90aW1lID0gdGltZS50aW1lKCkKICAgIHdpdGggSW1hZ2Uub3BlbihyZWFkX2Jhc2U2NF9pbWFnZShpbWFnZV9vbGQpKSBhcyBpbToKICAgICAgICBpbSA9IEltYWdlT3BzLmdyYXlzY2FsZShpbSkKICAgICAgICBlbmNvZGVkID0gZW5jb2RlX2Jhc2U2NF9pbWFnZShpbSkKICAgICAgICBlbmRfdGltZSA9IHRpbWUudGltZSgpCiAgICAgICAgcHJpbnQoIlRpbWU6IiwgZW5kX3RpbWUgLSBzdGFydF90aW1lKQogICAgICAgIHJldHVybiBlbmNvZGVkCg==",
        "requirements": "cmVkaXMKcHN5Y29wZzIKcGlsbG93"
    }
    data.update(COMMON_VALUES)
    return data

def get_testmatrix_data():
    data= {
        "fnName": "testmatrix",
        "bucketName": "testmatrix",
        "sourceCode": "IyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMKIyBBZGQgeW91ciBpbXBvcnRzIGhlcmUKIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMKaW1wb3J0IG51bXB5IGFzIG5wCmltcG9ydCB0aW1lCgojIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjCiMgRW50ZXIgeW91IEJ1Y2tldCBuYW1lIGhlcmUKIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIwpCVUNLRVRfTkFNRSA9ICJ0ZXN0bWF0cml4IgoKIyBEbyBub3QgZWRpdCB0aGlzIGZ1bmN0aW9uIG5hbWUKZGVmIHVzZXJEZWZpbmVkRnVuY3Rpb24oaW1hZ2Vfb2xkKToKICAgIHN0YXJ0X3RpbWUgPSB0aW1lLnRpbWUoKQogICAgbWF0cml4MSA9IG5wLnJhbmRvbS5yYW5kKDIwMDAsIDIwMDApCiAgICBtYXRyaXgyID0gbnAucmFuZG9tLnJhbmQoMjAwMCwgMjAwMCkKICAgIHJlc3VsdCA9IG5wLmRvdChtYXRyaXgxLCBtYXRyaXgyKQogICAgZW5kX3RpbWUgPSB0aW1lLnRpbWUoKQogICAgcHJpbnQoIlRpbWU6IiwgZW5kX3RpbWUgLSBzdGFydF90aW1lKQogICAgcmV0dXJuIGltYWdlX29sZAo=",
        "requirements": "cmVkaXMKcHN5Y29wZzIKbnVtcHk="
    }
    data.update(COMMON_VALUES)
    return data


def get_user_input(prompt):
    return input(prompt)

def call_endpoint(payload):
    url = 'http://localhost:8005/testfaas/runTest'
    response = requests.post(url, json=payload)
    return response

def read_csv(filename, start_range, end_range, step_size):
    data = {'load': [], 'response_time': [], 'throughput': []}
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data['load'].append(int(row['Load']))
            data['response_time'].append(float(row['Response Time (sec)']))
            data['throughput'].append(float(row['Throughput (per sec)']))

    # Rename the file with its load range
    #archive_folder = "../logs/archive/"
    #new_filename = f"test_{start_range}-{end_range}-{step_size}.csv"
    #os.rename(filename, os.path.join(archive_folder, new_filename))

    return data


def plot_graphs(initial_load, final_load, step_size, *data_dicts):
    colors = ['orange', 'green', 'blue']  # Different colors for different test types
    legends = ['testlog', 'testgray', 'testmatrix']  # Hardcoded legends for test types

    plt.figure(figsize=(10, 5))

    for i, (data_dict, legend) in enumerate(zip(data_dicts, legends)):
        plt.plot(data_dict['load'], data_dict['response_time'], label=legend, color=colors[i])

    plt.xlabel('Load (numbers of units to be processed)')
    plt.ylabel('Response Time (sec)')
    plt.title('Load vs Response Time')
    plt.legend()
    plt.ylim(0)
    plt.grid(True)
    plt.savefig(f'response_time_graph_{initial_load}_{final_load}_{step_size}.png')
    plt.show()

    plt.figure(figsize=(10, 5))
    for i, (data_dict, legend) in enumerate(zip(data_dicts, legends)):
        plt.plot(data_dict['load'], data_dict['throughput'], label=legend, color=colors[i])

    plt.xlabel('Load (numbers of units to be processed)')
    plt.ylabel('Throughput (per sec)')
    plt.title('Load vs Throughput')
    plt.legend()
    plt.ylim(0)
    plt.grid(True)
    plt.savefig(f'throughput_graph_{initial_load}_{final_load}_{step_size}.png')
    plt.show()



def main():
    initial_load = int(get_user_input("Provide the initial load of the load test range: "))
    final_load = int(get_user_input("Provide the final load of the load test range: "))
    step_size = int(get_user_input("Provide the step size for load increase: "))
#    test_type = get_user_input("Which type of test do you want to run?\nChoose from the below options:\n1) testlog\n2) testgray\n3) testmatrix\n")
	

	 # Initialize dictionaries to store data for each test type
    testlog_data = {'load': [], 'response_time': [], 'throughput': []}
    testgray_data = {'load': [], 'response_time': [], 'throughput': []}
    testmatrix_data = {'load': [], 'response_time': [], 'throughput': []}

    filename = "../logs/test.csv"

    loads = list(range(initial_load, final_load + 1, step_size))
    for load in loads:
        for test_type, data in [("testlog", testlog_data), ("testgray", testgray_data), ("testmatrix", testmatrix_data)]:
            print(f"Test with load: {load} and test type: {test_type}")
            if test_type == "testlog":
                payload = get_testlog_data()
            elif test_type == "testgray":
                payload = get_testgray_data()
            elif test_type == "testmatrix":
                payload = get_testmatrix_data()

            payload["loadCount"] = load
            call_endpoint(payload)
            time.sleep(2)

            # Append data to the respective test type dictionary
            data['load'].append(load)

    # Read data from CSV for each test type
    for data, test_type in [(testlog_data, "testlog"), (testgray_data, "testgray"), (testmatrix_data, "testmatrix")]:
        csv_filename = f"../logs/{test_type}.csv"
        test_data = read_csv(csv_filename, initial_load, final_load, step_size)
        data.update(test_data)

    # Plot graphs for each test type
    plot_graphs(initial_load,final_load,step_size,testlog_data, testgray_data, testmatrix_data)


if __name__ == "__main__":
    main()
