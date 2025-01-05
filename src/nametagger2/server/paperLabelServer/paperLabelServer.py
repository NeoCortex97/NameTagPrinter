import atexit
import datetime
import queue
import threading
from queue import Queue
from time import sleep

import zmq

from paperLabelServer.config.paperLabelConfig import BadgeServerConfig
from jobs.badgeJob import Job
from paperLabelServer.drivers.brotherQLDriver import BadgeDriver

context = zmq.Context()
socket = context.socket(zmq.REP)
boot = datetime.datetime.now()


class NameMissingError(Exception):
    pass


class BadgeWorker(threading.Thread):
    def __init__(self, queue: Queue[Job], driver: BadgeDriver):
        threading.Thread.__init__(self, name='BadgeWorker')
        self.running: bool = False
        self.queue: Queue[Job] = queue
        self.driver = driver

    def start(self):
        self.running = True
        threading.Thread.start(self)

    def run(self):
        while self.running:
            while self.queue.empty():
                sleep(0.25)
            job: Job = self.queue.get()
            self.driver.process(job)

    def stop(self):
        self.running = False


worker: BadgeWorker


def close():
    worker.stop()
    socket.close()
    context.destroy()


def parse_job(serialized: str, config) -> Job:
    parts = serialized.strip().split(';')
    params = {part.split('=')[0].upper(): part.split('=')[1] for part in parts}
    if 'NAME' not in params.keys():
        raise NameMissingError()
    if 'LOGO' not in params.keys() and 'SPACE' in params.keys() and params['SPACE'] in config.logos.keys():
        params['LOGO'] = params['SPACE']
    if 'LOGO' in params.keys() and params['LOGO'] not in config.logos.keys():
        params['LOGO'] = config.default_logo

    params['LOGO'] = config.logos[params['LOGO']]
    params = {key.lower(): value for key, value in params.items()}
    return Job(**params)


def main():
    global worker
    config = BadgeServerConfig()
    print(f'binding to {config.connection_string}')
    socket.bind(config.connection_string)

    driver = BadgeDriver()
    driver.printer_config = config.printer
    driver.badge_config = config.badge

    badge_queue = Queue(maxsize=config.queue_size)

    worker = BadgeWorker(badge_queue, driver)
    worker.start()

    while True:
        message = socket.recv().decode('utf-8')
        try:
            command = message.strip().split(';')[0]
            match command.upper():
                case 'ADD':
                    job = parse_job(';'.join(message.split(';')[1:]), config.badge)
                    badge_queue.put(job, timeout=config.timeout)
                    print(job)
                    socket.send(f'OK;jod_id={job.id};position={badge_queue.qsize()}'.encode('utf-8'))
                case 'STATUS':
                    socket.send(b'NOT_IMPLEMENTED;message=this feature is currently not implemented')
                case 'ABORT':
                    socket.send(b'NOT_IMPLEMENTED;message=this feature is currently not implemented')
                case 'LENGTH':
                    socket.send(b'NOT_IMPLEMENTED;message=this feature is currently not implemented')
                case 'ALIVE':
                    socket.send(b'OK')
                case 'UPTIME':
                    socket.send(str(datetime.datetime.now() - boot).encode('utf-8'))
        except NameMissingError:
            socket.send(b'FORMAT_ERROR;message=missing Name')
        except queue.Full:
            socket.send(b'QUEUE_ERROR;message=Queue full - Try again later')


atexit.register(close)


if __name__ == '__main__':
    main()
