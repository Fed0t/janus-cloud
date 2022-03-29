# -*- coding: utf-8 -*-
import logging
import sys
from januscloud.backup import worker
from januscloud.backup.config import load_conf
from watchdog.observers.polling import PollingObserver

from januscloud.backup.watchdog_handler import Handler

log = logging.getLogger(__name__)


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


