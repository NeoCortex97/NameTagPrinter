import zmq

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    ip = input('IP: ')
    print('connection to socket ...', end='')
    socket.connect(f'tcp://{ip}:6660')
    print('OK')

    while True:
        socket.send(input('> ').encode('utf-8'))
        print(socket.recv_string())


if __name__ == '__main__':
    main()