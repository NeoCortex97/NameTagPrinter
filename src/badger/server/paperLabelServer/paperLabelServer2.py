import asyncio
import json
from asyncio import Queue

import zmq.asyncio
from netifaces import interfaces, ifaddresses, AF_INET
from zmq import ZMQError

from badger.server.config.exceptions import NotAConfigSectionError, NotASettingError
from badger.server.jobs.job import Job
from badger.server.jobs.rasterJob import RasterJob
from badger.server.jobs.util import parse_job
from badger.server.paperLabelServer.config.paperLabelConfig import PaperLabelConfig
from badger.server.paperLabelServer.drivers.brotherQLDriver import BrotherQLDriver
from badger.server.paperLabelServer.processors import get_processors

context = zmq.asyncio.Context()

command_socket = context.socket(zmq.REP)
job_stream = context.socket(zmq.PULL)
update_stream = context.socket(zmq.PUSH)

update_state = False
job_state = False
running = True

config = PaperLabelConfig()

loop = asyncio.new_event_loop()
update_queue: Queue = Queue()
raw_job_queue: Queue[Job] = Queue()
job_queue: Queue[RasterJob] = Queue()


async def worker():
    driver = BrotherQLDriver()
    while running:
        job = await job_queue.get()
        driver.process(job)


async def execute_config_command(params: list[str]):
    match params[1].lower():
        case 'set':
            try:
                config.overwrite(params[2:])
                await command_socket.send_string('OK')
            except NotAConfigSectionError as e:
                await command_socket.send_string(
                    f'ERROR_{e.id};"{e.section}" is not a valid config section for this service.')
            except NotASettingError as e:
                await command_socket.send_string(
                    f'ERROR_{e.id};There is not key "{e.setting}" to set to "{e.value}" in section "{e.section}".')
        case 'get':
            try:
                await command_socket.send_string('OK;' + json.dumps(config.get(params[2:])))
            except NotAConfigSectionError as e:
                await command_socket.send_string(
                    f'ERROR_{e.id};"{e.section}" is not a valid config section for this service.')
            except NotASettingError as e:
                await command_socket.send_string(
                    f'ERROR_{e.id};There is no setting "{e.setting}" in section "{e.section}".')
        case _:
            await command_socket.send_string('OK; UNKNOWN')


async def execute_general_command(params: list[str]):
    match params[1].lower():
        case 'job_stream':
            match params[2].lower():
                case 'enable':
                    enable_job_stream()
                case 'disable':
                    disable_job_stream()
                case 'state':
                    await command_socket.send_string(f'OK;{str(job_state).upper()}')
        case 'update_stream':
            match params[2].lower():
                case 'enable':
                    enable_update_stream()
                case 'disable':
                    disable_update_stream()
                case 'state':
                    await command_socket.send_string(f'OK;{str(update_state).upper()}')
        case 'id':
            await command_socket.send_string(f'OK;{config.instance_id}')
    try:
        await  command_socket.send_string('OK')
    except ZMQError:
        pass


async def execute_job_command(params: list[str]):
    await command_socket.send_string('OK')


async def execute_queue_command(params: list[str]):
    await command_socket.send_string('OK')


async def execute_ping_command(params: list[str]):
    await command_socket.send_string('PONG')


async def parse_and_process_commands():
    while running:
        message: str = await command_socket.recv_string()
        parts = message.split(' ')
        match parts[0].lower():
            case 'config':
                await execute_config_command(parts)
            case 'command':
                await execute_general_command(parts)
            case 'job':
                await execute_job_command(parts)
            case 'queue':
                await execute_queue_command(parts)
            case 'ping':
                await execute_ping_command(parts)
            case _:
                await command_socket.send_string('UNKNOWN_COMMAND')


async def accept_jobs():
    while running:
        print('Waiting to receive new Job')
        message = await job_stream.recv_string()
        job = parse_job(message)
        print(f'Pushing job {job.id}')
        await raw_job_queue.put(job)


async def push_updates():
    while running:
        update = await update_queue.get()
        await update_stream.send_string(update)


def enable_job_stream():
    global job_state
    print('Job stream enabled')
    if '*' in config.job_steam_connection:
        connect_to_all_interfaces(job_stream, int(config.job_steam_connection.split(':')[-1]))
    else:
        job_stream.connect(config.job_steam_connection)
    loop.create_task(accept_jobs(), name='Job Acceptor')
    job_state = True


def enable_update_stream():
    global update_state
    print('Update stream enabled')
    if '*' in config.update_stream_connection:
        connect_to_all_interfaces(update_stream, int(config.update_stream_connection.split(':')[-1]))
    else:
        update_stream.connect(config.update_stream_connection)
    loop.create_task(push_updates(), name='Update dispatcher')
    update_state = True


async def process_job():
    global running
    print('Job processing started')
    while running:
        print('Waiting to process new Job')
        job = await raw_job_queue.get()
        print('Processing new job')
        for processor in get_processors():
            print(f'trying {processor.__name__}')
            p = processor()
            if p.is_applicable(job):
                print(f'Found processor for job {job.id}')
                incomplete, complete = p.apply(job)
                if incomplete is not None:
                    await raw_job_queue.put(incomplete)
                elif complete is not None:
                    await job_queue.put(complete)
                break
        else:
            print(f'No processor for job {job.id}')


def connect_to_all_interfaces(sock: zmq.Socket, port: int):
    for interface in interfaces():
        try:
            for link in ifaddresses(interface)[AF_INET]:
                print(f'Connecting {link["addr"]}:{port} on socket.')
                sock.connect(f'tcp://{link["addr"]}:{port}')
        except KeyError:
            pass

def disconnect_from_all_interfaces(sock:zmq.Socket, port: int):
    for interface in interfaces():
        try:
            for link in ifaddresses(interface)[AF_INET]:
                print(f'Disconnecting {link["addr"]}:{port} on socket.')
                sock.disconnect(f'tcp://{link["addr"]}:{port}')
        except KeyError:
            pass


def main():
    hello_socket = context.socket(zmq.PUSH)
    connect_to_all_interfaces(hello_socket, 6062)

    hello_socket.send_string(str(config.instance_id))
    command_socket.bind(config.command_connection)

    if config.job_stream_enabled:
        enable_job_stream()

    if config.update_stream_enabled:
        enable_update_stream()

    loop.create_task(process_job(), name='Job Processing')

    loop.run_until_complete(parse_and_process_commands())


if __name__ == '__main__':
    print(f'ZeroMQ Version: {zmq.zmq_version()}')
    print(f'Pyzmq Version: {zmq.pyzmq_version()}')
    print(f'Instance ID: {config.instance_id.hex}')
    main()
