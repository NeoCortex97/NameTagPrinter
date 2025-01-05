import pathlib
import sys

import zmq

def main(argv):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    ip = input('IP: ')
    print('connection to socket ...', end='')
    socket.connect(f'tcp://{ip}:6660')
    print('OK')

    if len(argv) > 1:
        for file in argv[1:]:
            with pathlib.Path(file).open('r') as f:
                for cmd in f.readlines():
                    print(cmd.strip(), '...', end='')
                    socket.send(cmd.strip().encode('utf-8'))
                    print(socket.recv().decode('utf-8'))


if __name__ == '__main__':
    main(sys.argv)