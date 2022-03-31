from redis import Redis
from rq import Queue, Worker
import uuid


def start_worker(config):
    connection_pool = Redis.BlockingConnectionPool.from_url(
        url=config['janus']['redis_connection'],
        decode_responses=True,
        health_check_interval=30,
        timeout=10)
    redis = Redis(connection_pool=connection_pool)
    queue = Queue(config['janus']['queue_name'] + str(uuid.getnode()), connection=redis)
    worker = Worker([queue], connection=redis)
    worker.work()
