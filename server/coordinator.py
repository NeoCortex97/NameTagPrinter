import zmq

from config.coordinatorConfig import CoordinatorConfig

context = zmq.Context()
badge_socket = context.socket(zmq.REQ)
receipt_socket = context.socket(zmq.REQ)
# display_socket = context.socket(zmq.REQ) # No hardware, so not implementing yet
frontend_socket = context.socket(zmq.REP)


class InvalidCommandError(Exception):
    pass


class EmptyCommandError(Exception):
    pass


class MissingActionError(Exception):
    pass


class Command:
    def __init__(self):
        self.destination: str = ''
        self.action: str = ''
        self.params: dict = {}

    def parse(self, message: str):
        parts = message.strip().split(';')
        self.destination = parts[0].lower()
        if self.destination.lower() not in 'badge receipt'.split(' '):
            raise InvalidCommandError()

        params = {item.split('=')[0].lower(): item.split('=')[1] for item in parts[1:]}
        if len(params) < 1:
            raise EmptyCommandError()
        if 'action' not in [i.lower() for i in params.keys()]:
            raise MissingActionError()

        self.action = params['action']

        self.params = {key: value for key, value in params.items() if key.lower() != 'action'}

    def encode(self) -> bytes:
        return (f'{self.action.upper()};' + ';'.join([f"{key}={value}" for key, value in self.params.items()])).encode('utf-8')

    def __repr__(self):
        return f'Send "{self.action}" to {self.destination} ({", ".join([key + '=' + value for key, value in self.params.items()])})'



def main():
    config = CoordinatorConfig()
    frontend_socket.bind(config.frontend_connection_string)
    badge_socket.connect(config.badge_connection_string)
    receipt_socket.connect(config.receipt_connetion_string)

    while True:
        message = frontend_socket.recv().decode('utf-8')

        try:
            command = Command()
            command.parse(message)

            print(command)
            if command.destination == 'badge':
                badge_socket.send(command.encode())
                response = badge_socket.recv()
                frontend_socket.send(response)
            elif command.destination == 'receipt':
                frontend_socket.send_string('OG')
            else:
                frontend_socket.send_string(message)
        except InvalidCommandError:
            frontend_socket.send_string('FAIL;error=invallid topic;message=First segment should either be one of badge, receipt')
        except EmptyCommandError:
            frontend_socket.send_string('OK')
        except MissingActionError:
            frontend_socket.send_string('WARN;message=an action is needed to execute command. This did nothing')


if __name__ == '__main__':
    main()
