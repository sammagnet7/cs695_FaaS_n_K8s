import requests

BASE = "http://localhost:8003/"
RAPI = "api/v1/register"
DAPI = "api/v1/dispatch"
SAPI = "api/v1/status/"
headers = {"Content-type": "multipart/form-data", "Accept": "*"}

add_files = [
    ("file", ("image.png", open("test/image.png", "rb"), "image/png")),
    ("file", ("image2.png", open("test/image2.png", "rb"), "image/png")),
    ("file", ("requirements.txt", open("test/requirements.txt", "rb"), "text/plain")),
]


def post_file_contents(url):

    response = requests.post(
        url,
        json={
            "fnName": "kappa",
            "runtime": "python",
            "sourceCode": "cHJpbnQoIkhlbGxvIFdvcmxkISIp",
        },
        # headers=headers,
    )
    return response


# response = post_file_contents(BASE + RAPI)
# print(response)
# response = requests.delete(BASE + API, json={"id": 1}, headers=headers)
# response = requests.post(BASE + DAPI, json={"name": "blur-test", "type": "python"})
# print(response)
response = requests.get(BASE + SAPI)
print(response.json())
