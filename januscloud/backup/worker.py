from redis import Redis
from rq import Queue, Worker
import uuid

def start_worker(config):
    redis = Redis.from_url(config['janus']['redis_connection'])
    queue = Queue(config['janus']['queue_name'] + str(uuid.getnode()), connection=redis)
    worker = Worker([queue], connection=redis)
    worker.work()
