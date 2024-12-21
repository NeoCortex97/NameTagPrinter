import zmq

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    print('connection to socket ...', end='')
    socket.connect('tcp://192.168.178.122:6660')
    print('OK')
    while True:
        name = input('name: ')
        space = input('space: ')
        logo = input('logo: ')
        url = input('website: ')

        print('processing request ...', end='')
        socket.send(f'TAG;{name};{space};{logo};{url}'.encode('utf-8'))
        print(socket.recv().decode('utf-8'))
        print('Processing receipt ...', end='')
        socket.send(f'RECEIPT;{name};{space};{logo};{url}'.encode('utf-8'))
        print(socket.recv().decode('utf-8'))
        print('#' * 80)



if __name__ == '__main__':
    main()