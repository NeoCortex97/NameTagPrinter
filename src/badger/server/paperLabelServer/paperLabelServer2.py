import asyncio
import json
from asyncio import Queue

import zmq.asyncio
from netifaces import interfaces, ifaddresses, AF_INET

from badger.server.config.exceptions import NotAConfigSectionError, NotASettingError
from badger.server.jobs.job import Job, JobType
from badger.server.jobs.rasterJob import RasterJob
from badger.server.jobs.util import parse_job
from badger.server.paperLabelServer.config.paperLabelConfig import PaperLabelConfig
from badger.server.paperLabelServer.drivers.brotherQLDriver import BrotherQLDriver
from badger.server.paperLabelServer.processors.rasterProcessor import RasterProcessor
from badger.server.paperLabelServer.processors.rawProcessor import RawProcessor
from badger.server.paperLabelServer.processors.scriptProcessor import ScriptProcessor
from badger.server.paperLabelServer.processors.templateProcessor import TemplateProcessor
from badger.server.processors.jobProcessor import JobProcessor

context = zmq.asyncio.Context()

command_socket = context.socket(zmq.REP)
job_stream = context.socket(zmq.PULL)
update_stream = context.socket(zmq.PUSH)

config = PaperLabelConfig()

running = True

loop = asyncio.new_event_loop()
update_queue: Queue = Queue()
raw_job_queue: Queue[Job] = Queue()
job_queue: Queue[RasterJob] = Queue()


processors = [
    RawProcessor(),
    RasterProcessor(),
    TemplateProcessor(),
    ScriptProcessor(),
]


def disable_job_stream():
    global job_stream
    job_stream.close()
    job_stream = context.socket(zmq.PULL)


def disable_update_stream():
    global update_stream
    global context
    update_stream.close()
    update_stream = context.socket(zmq.PUSH)

async def worker():
    driver = BrotherQLDriver()
    while running:
        job = await job_queue.get()
        driver.process(job)



async def parse_and_process_commands():
    while running:
        message: str = await command_socket.recv_string()
        parts = message.split(' ')
        match parts[0].lower():
            case 'config':
                match parts[1].lower():
                    case 'set':
                        try:
                            config.overwrite(parts[2:])
                            await command_socket.send_string('OK')
                        except NotAConfigSectionError as e:
                            await command_socket.send_string(f'ERROR_{e.id};"{e.section}" is not a valid config section for this service.')
                        except NotASettingError as e:
                            await command_socket.send_string(f'ERROR_{e.id};There is not key "{e.setting}" to set to "{e.value}" in section "{e.section}".')
                    case 'get':
                        try:
                            await command_socket.send_string('OK;' + json.dumps(config.get(parts[2:])))
                        except NotAConfigSectionError as e:
                            await command_socket.send_string(f'ERROR_{e.id};"{e.section}" is not a valid config section for this service.')
                        except NotASettingError as e:
                            await command_socket.send_string(f'ERROR_{e.id};There is no setting "{e.setting}" in section "{e.section}".')
                    case _:
                        await command_socket.send_string('OK; UNKNOWN')
            case 'command':
                match parts[2].lower():
                    case 'job_stream':
                        match parts[3].lower():
                            case 'enable':
                                enable_job_stream()
                            case 'disable':
                                disable_job_stream()
                await  command_socket.send_string('OK')
            case 'job':
                await command_socket.send_string('OK')
            case 'queue':
                await command_socket.send_string('OK')
            case 'ping':
                await command_socket.send_string('PONG')
            case _:
                await command_socket.send_string('UNKNOWN_COMMAND')


async def accept_jobs():
    while running:
        message = await job_stream.recv_string()
        job = parse_job(message)
        await raw_job_queue.put(job)
        print(message)


async def push_updates():
    while running:
        update = await update_queue.get()
        await update_stream.send_string(update)


def enable_job_stream():
    print('Job stream enabled')
    job_stream.bind(config.job_steam_connection)
    loop.create_task(accept_jobs())


def enable_update_stream():
    print('Update stream enabled')
    update_stream.bind(config.update_stream_connection)
    loop.create_task(push_updates())


async def process_job():
    while running:
        job = await raw_job_queue.get()
        for processor in processors:
            if processor.is_applicable(job):
                incomplete, complete = processor.apply(job)
                if incomplete is not None:
                    await raw_job_queue.put(incomplete)
                else:
                    await job_queue.put(complete)
                break


def main():
    hello_socket = context.socket(zmq.PUSH)
    for interface in interfaces():
        try:
            for link in ifaddresses(interface)[AF_INET]:
                print(link)
                hello_socket.connect(f'tcp://{link["addr"]}:6062')
        except KeyError:
            pass

    hello_socket.send_string(str(config.instance_id))
    command_socket.bind(config.command_connection)

    if config.job_stream_enabled:
        enable_job_stream()

    if config.update_stream_enabled:
        enable_update_stream()

    loop.create_task(process_job())

    loop.run_until_complete(parse_and_process_commands())


if __name__ == '__main__':
    print(f'ZeroMQ Version: {zmq.zmq_version()}')
    print(f'Pyzmq Version: {zmq.pyzmq_version()}')
    main()
