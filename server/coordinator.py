import zmq


context = zmq.Context()
badge_socket = context.socket(zmq.REQ)
receipt_socket = context.socket(zmq.REQ)
display_socket = context.socket(zmq.REQ)
frontend_socket = context.socket(zmq.REP)


def main():
    pass


if __name__ == '__main__':
    main()
