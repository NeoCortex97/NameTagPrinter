import threading
from typing import Dict, Any

import zmq
from zmq.utils.monitor import recv_monitor_message

context = zmq.Context()
socket = context.socket(zmq.REP)
monitor = socket.get_monitor_socket(zmq.EVENT_ALL)

EVENT_MAP = {}
print("Event names:")
for name in dir(zmq):
    if name.startswith('EVENT_'):
        value = getattr(zmq, name)
        print(f"{name:21} : {value:4}")
        EVENT_MAP[value] = name


def event_monitor(monitor: zmq.Socket) -> None:
    while monitor.poll():
        evt: Dict[str, Any] = {}
        mon_evt = recv_monitor_message(monitor)
        evt.update(mon_evt)
        evt['description'] = EVENT_MAP[evt['event']]
        print(f"Event: {evt}")
        if evt['event'] == zmq.EVENT_MONITOR_STOPPED:
            break
    monitor.close()
    print()
    print("event monitor thread done!")

t = threading.Thread(target=event_monitor, args=(monitor,))
t.start()

socket.bind('tcp://*:5555')

while True:
    message = socket.recv()
    socket.send(message)