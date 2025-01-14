import asyncio

import zmq.asyncio


ctx = zmq.asyncio.Context()


async def work():
    sock = ctx.socket(zmq.REP)
    sock.bind('tcp://*:5000')
    running = True
    while running:
        msg = await sock.recv_string()
        print(msg)
        if msg.lower() == 'stop':
            running = False
        await sock.send_string(msg)


def main():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(work())


if __name__ == '__main__':
    main()
