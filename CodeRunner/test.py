from datetime import datetime
from time import sleep
import redis

REDIS_HOST = "10.157.3.213"
REDIS_PORT = "6379"
job_name = ""
bucket_id = ""
redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
queue_name = f"{job_name}_{bucket_id}_queue"


def get_current_redis_queue_size(queue_name: str):
    try:
        queue_size = redis_conn.llen(queue_name)
        return queue_size
    except Exception as e:
        print(f"Error getting size of Redis queue {queue_name}: {e}")
        return None


for i in range(0, 360):
    print(
        f"Items in queue {queue_name}: {get_current_redis_queue_size(queue_name)} counter-{i}"
    )
    sleep(0.5)
