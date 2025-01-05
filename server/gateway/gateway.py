import threading
import uuid
from queue import Queue
from threading import Thread
from time import sleep

import zmq
import logging

__VERSION__ = '1.0'

from gateway.config.coordinatorConfig import CoordinatorConfig

log = logging.getLogger(__name__)
context = zmq.Context()
badge_socket = context.socket(zmq.REQ)
receipt_socket = context.socket(zmq.REQ)
display_socket = context.socket(zmq.REQ) # No hardware, so not implementing yet
frontend_socket = context.socket(zmq.REP)


class InvalidCommandError(Exception):
    pass


class EmptyCommandError(Exception):
    pass


class MissingActionError(Exception):
    pass


class Command:
    def __init__(self):
        self.destination: str = ''
        self.action: str = ''
        self.params: dict = {}
        self.id = uuid.uuid4()

    def parse(self, message: str):
        parts = message.strip().split(';')
        self.destination = parts[0].lower()
        if self.destination.lower() not in 'badge receipt'.split(' '):
            raise InvalidCommandError()

        params = {item.split('=')[0].lower(): item.split('=')[1] for item in parts[1:]}
        if len(params) < 1:
            raise EmptyCommandError()
        if 'action' not in [i.lower() for i in params.keys()]:
            raise MissingActionError()

        self.action = params['action']

        self.params = {key: value for key, value in params.items() if key.lower() != 'action'}

    def encode(self) -> bytes:
        return (f'{self.action.upper()};' + ';'.join([f"{key}={value}" for key, value in self.params.items()])).encode('utf-8')

    def __repr__(self):
        return f'Send "{self.action}" to {self.destination} ({", ".join([key + '=' + value for key, value in self.params.items()])})'


class Worker(Thread):
    def __init__(self, buffer_size: int, socket: zmq.Socket):
        threading.Thread.__init__(self, name='BadgeWorker')
        self.running: bool = False
        self.queue: Queue[Command] = Queue(buffer_size)
        self.socket: zmq.Socket = socket

    def start(self):
        self.running = True
        threading.Thread.start(self)

    def stop(self):
        self.running = False

    def push(self, command: Command) -> uuid.UUID:
        self.queue.put(command)
        return command.id

    def run(self):
        while self.running:
            if self.queue.empty():
                sleep(0.5)
                continue
            cmd: Command = self.queue.get()
            print(cmd)
            self.socket.send(cmd.encode())




def main():
    logging.basicConfig(level=logging.INFO)
    log.info(f'LabelCluster module COORDINATOR (version: {__VERSION__})')
    config = CoordinatorConfig()
    log.debug('Setting up sockets')
    badge_socket.connect(config.badge_connection_string)
    receipt_socket.connect(config.receipt_connetion_string)
    display_socket.connect(config.display_connection_string)
    frontend_socket.bind(config.frontend_connection_string)
    log.debug('Sockets ready')

    # log.debug('Creating workers ...')
    # badge_worker = Worker(config.badge_queue_size, badge_socket)
    # receipt_worker = Worker(config.receipt_queue_size, receipt_socket)
    # display_worker = Worker(config.display_queue_size, display_socket)
    # log.debug('Workers created')
    #
    # log.debug('Starting workers ...')
    # badge_worker.start()
    # receipt_worker.start()
    # display_worker.start()
    # log.info('Workers started')

    while True:
        message = frontend_socket.recv().decode('utf-8')
        log.debug(message)

        try:
            command = Command()
            command.parse(message)

            print(command)
            if command.destination == 'badge':
                badge_socket.send(command.encode())
                frontend_socket.send(badge_socket.recv())
            elif command.destination == 'receipt':
                frontend_socket.send_string('OG')
            else:
                frontend_socket.send_string(message)
        except InvalidCommandError:
            frontend_socket.send_string('FAIL;error=invallid topic;message=First segment should either be one of badge, receipt')
        except EmptyCommandError:
            frontend_socket.send_string('OK')
        except MissingActionError:
            frontend_socket.send_string('WARN;message=an action is needed to execute command. This did nothing')


if __name__ == '__main__':
    main()
