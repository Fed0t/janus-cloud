from redis import Redis
from rq import Queue
from watchdog.events import FileSystemEventHandler
from januscloud.backup.providers.mux_uploader import backup_event
import subprocess
import uuid
PROVIDER = 1


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
