import asyncio
from abc import ABC
from asyncio import AbstractEventLoop
from collections.abc import Callable, Awaitable
from queue import Queue
from typing import Any

import zmq
from zmq.asyncio import Poller

from badger.server.config.ServiceConfig import ServiceConfig


class AsyncService(ABC):
    def __init__(self, config: ServiceConfig, loop: AbstractEventLoop, name: str = 'Service'):
        self.task: asyncio.Task = None
        self.running: bool = False
        self.on_enable: Callable[*Any, Any] = None
        self.on_disable: Callable[*Any, Any] = None
        self.worker: Callable[[Any], Awaitable[Any]] = None
        self.config: ServiceConfig = config
        self.name = name
        self.loop = loop

    def enable(self) -> None:
        self.running = True
        if hasattr(self, 'housekeeping_enable'):
            self.housekeeping_enable()
        if self.on_enable is not None:
            self.on_enable()
        self.task = self.loop.create_task(self.worker(self.config), name = self.name)

    def disable(self) -> None:
        self.running = False
        if hasattr(self, 'housekeeping_disable'):
            self.housekeeping_disable()
        if self.on_disable is not None:
            self.on_disable()
        self.task.cancel()

    def is_running(self) -> bool:
        return self.running and self.loop.is_running()

class AsyncZmqService(AsyncService):
    def __init__(self, config: ServiceConfig, loop: AbstractEventLoop, socket: zmq.Socket, name: str = 'Service', input_queue: Queue = Queue(), output_queue: Queue = Queue()):
        super().__init__(config, loop, name)
        self.socket = socket
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.connections: list[str] = []

    def housekeeping_enable(self):
        for url in self.connections:
            self.socket.connect(url)

    def housekeeping_disable(self):
        for url in self.connections:
            self.socket.disconnect(url)

    def connect(self, url: str):
        if self.running:
            self.socket.connect(url)
        if url not in self.connections:
            self.connections.append(url)

    def disconnect(self, url: str):
        if self.running:
            self.socket.disconnect(url)
        if url in self.connections:
            self.connections.remove(url)

    def register_connection(self, url: str):
        if url not in self.connections:
            self.connections.append(url)

    def unregister_connections(self, url: str):
        if url in self.connections:
            self.connections.remove(url)


class ZmqCommandService(AsyncZmqService):
    def __init__(self, config: ServiceConfig, loop: AbstractEventLoop, socket: zmq.Socket, name: str = 'Service', input_queue: Queue = Queue(), output_queue: Queue = Queue()):
        super().__init__(config, loop, socket, name, input_queue, output_queue)
        self.worker = self.command_handler
        self.handlers: dict = {}

    def command_handler(self):
        poller = Poller()
        poller.register(self.socket, flags=zmq.POLLIN)
        while self.running:
            poll_result = poller.poll(1000)
            if poll_result == zmq.POLLIN:
                command = self.socket.recv_string().split(' ')
                hdlr = self.handlers
                offset = 0
                for cmd in command:
                    if cmd not in hdlr.keys():
                        self.socket.send_string(f'ERROR;UNKNOWN_COMMAND')
                        break
                    if type(hdlr[cmd]) is not Callable:
                        hdlr = hdlr[cmd]
                        offset += 1
                    else:
                        break

                hdlr[offset - 1](self.input_queue, self.output_queue, self.config, command[offset:])

    def register_handler(self, *cmds : str, handler: Callable):
        hdlr = self.handlers
        for index, item in enumerate(cmds):
            if index != len(cmds)-1:
                if item not in hdlr.keys():
                    hdlr[item] = {}
                hdlr = hdlr[item]
        hdlr[cmds[-1]] = handler
