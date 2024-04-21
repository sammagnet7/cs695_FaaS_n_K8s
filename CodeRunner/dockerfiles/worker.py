# Just prints standard out and sleeps for 10 seconds.
import time
import os

url = os.getenv("BROKER_URL")
queue = os.environ.get("QUEUE")
print(f"Redis Queue {queue} URL: {url}")
