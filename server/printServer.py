from time import sleep

import zmq

from printer.badgeDriver import BadgeDriver

context = zmq.Context()

socket = context.socket(zmq.REP)
socket.bind('tcp://127.0.0.1:6660')
print('listening on tcp://127.0.0.1:6660')

badge_driver = BadgeDriver()

while True:
    message = socket.recv()
    print(message)

    command = message.decode('utf-8').split(';')

    if command[0].lower() == 'tag':
        badge_driver.print(command[1], command[2], command[3], command[4])
        socket.send(b'OK')
    elif command[0].lower() == 'receipt':
        sleep(1)
        socket.send(b'OK')  # Print receipt here
    elif command[0].lower() == 'stats':
        sleep(1)
        socket.send(b'OK')  # Print stats here
    elif command[0].lower() == 'reset':
        sleep(1)
        socket.send(b'OK')  # Reset Stats here
    else:
        socket.send(b'FAIL')
