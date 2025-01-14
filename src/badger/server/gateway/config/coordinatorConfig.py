import logging
import os

import dotenv

log = logging.getLogger(__file__)

class CoordinatorConfig:
    def __init__(self):
        log.debug('Loading config ...')
        dotenv.load_dotenv()

        self.coordinator_transport: str = os.getenv('COORDINATOR_TRANSPORT', 'tcp')
        self.coordinator_interface: str = os.getenv('COORDINATOR_INTERFACE', '0.0.0.0')
        self.coordinator_port: int = int(os.getenv('COORDINATOR_PORT', '6060'))
        self.badge_port: int = int(os.getenv('BADGE_SERVER_PORT', 6061))
        self.badge_interface: str = str(os.getenv('BADGE_SERVER_INTERFACE', '0.0.0.0'))
        self.badge_transport: str = str(os.getenv('BADGE_SERVER_TRANSPORT', 'tcp'))
        self.badge_queue_size: int = int(os.getenv('BADGE_SERVER_BUFFER_SIZE', 0))
        self.receipt_port: int = int(os.getenv('RECEIPT_SERVER_PORT', 6062))
        self.receipt_interface: str = str(os.getenv('RECEIPT_SERVER_INTERFACE', '0.0.0.0'))
        self.receipt_transport: str = str(os.getenv('RECEIPT_SERVER_TRANSPORT', 'tcp'))
        self.receipt_queue_size: int = int(os.getenv('RECEIPT_BUFFER_SIZE', 0))
        self.display_port: int = int(os.getenv('DISPLAY_PORT', 6063))
        self.display_interface: str = str(os.getenv('DISPLAY_INTERFACE', '0.0.0.0'))
        self.display_transport: str = str(os.getenv('DISPLAY_TRANSPORT', 'tcp'))
        self.display_queue_size: int = int(os.getenv('DISPLAY_BUFFER_SIZE', 0))
        log.debug('Config complete')

    @property
    def frontend_connection_string(self):
        return f'{self.coordinator_transport}://{self.coordinator_interface}:{self.coordinator_port}'

    @property
    def badge_connection_string(self) -> str:
        return f'{self.badge_transport}://{self.badge_interface}:{self.badge_port}'

    @property
    def receipt_connetion_string(self) -> str:
        return f'{self.receipt_transport}://{self.receipt_interface}:{self.receipt_port}'

    @property
    def display_connection_string(self):
        return f'{self.display_transport}://{self.display_interface}:{self.display_port}'