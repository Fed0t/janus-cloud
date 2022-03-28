# -*- coding: utf-8 -*-
import logging
import sys
import subprocess
import uuid

from januscloud.backup import worker
from januscloud.backup.config import load_conf
from redis import Redis
from rq import Queue
from januscloud.backup.providers.mux_uploader import backup_event
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

log = logging.getLogger(__name__)
PROVIDER = 1


def main():
    if len(sys.argv) == 2:
        config = load_conf(sys.argv[1])
    else:
        config = load_conf('/opt/janus-cloud/conf/janus-backup.yml')

    do_main(config)


def do_main(config):
    scan_folder(config)


def scan_folder(config):
    observer = PollingObserver()
    event_handler = Handler(config)
    observer.schedule(event_handler, config['janus']['recordings_dir'], recursive=True)
    observer.start()

    print('Started watchdog observer.', config['janus']['recordings_dir'])
    try:
        worker.start_worker(config)
    finally:
        observer.stop()
        observer.join()


class Handler(FileSystemEventHandler):

    def __init__(self, config):
        self.config = config

    def enqueue_job(self, event):
        redis = Redis.from_url(self.config['janus']['redis_connection'])
        queue = Queue(self.config['janus']['queue_name'] + str(uuid.getnode()), connection=redis)
        data = {'event': event, 'config': self.config}

        if PROVIDER == 1 and self.check_length(event.src_path, self.config['janus']['max_recording_seconds']):
            queue.enqueue(backup_event, data)

    @staticmethod
    def check_length(filename, max_length):
        try:
            result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                     "format=duration", "-of",
                                     "default=noprint_wrappers=1:nokey=1", filename],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            return float(result.stdout) >= float(max_length)
        except:
            return True

    def on_any_event(self, event):
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            self.enqueue_job(event)
            print("Received created event - %s." % event.src_path)
        elif event.event_type == 'modified':
            print("Received modified event - %s." % event.src_path)
