from time import sleep

import cups
import zmq
from cups import IPP_ERROR
from escpos.exceptions import DeviceNotFoundError

from drivers.badgeDriver import BadgeDriver
from drivers.receiptDriver import ReceiptDriver

context = zmq.Context()

socket = context.socket(zmq.REP)
socket.bind('tcp://0.0.0.0:6660')
print('listening on tcp://0.0.0.0:6660')

badge_driver = BadgeDriver()
receipt_driver = ReceiptDriver()

while True:
    message = socket.recv()
    print(message)

    command = message.decode('utf-8').split(';')

    if command[0].lower() == 'tag':
        try:
            badge_driver.print(command[1], command[2], command[3], command[4])
            socket.send(b'OK')
        except cups.IPPError as e:
            print(e)
            socket.send(f'FAIL;{e.args}'.encode('utf-8'))
    elif command[0].lower() == 'receipt':
            try:
                receipt_driver.print(command[1], command[2], command[3], command[4])
                socket.send(b'OK')  # Print receipt here
            except DeviceNotFoundError as e:
                print(e)
                socket.send(f'FAIL;{e.msg}'.encode('utf-8'))
    elif command[0].lower() == 'stats':
        sleep(1)
        socket.send(b'OK')  # Print stats here
    elif command[0].lower() == 'reset':
        sleep(1)
        socket.send(b'OK')  # Reset Stats here
    else:
        socket.send(b'FAIL')
