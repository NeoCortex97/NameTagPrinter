import os

import dotenv


class CoordinatorConfig:
    def __init__(self):
        dotenv.load_dotenv()

        self.coordinator_transport: str = os.getenv('COORDINATOR_TRANSPORT', 'tcp')
        self.coordinator_interface: str = os.getenv('COORDINATOR_INTERFACE', '0.0.0.0')
        self.coordinator_port: int = int(os.getenv('COORDINATOR_PORT', '6060'))
        self.badge_port: int = int(os.getenv('BADGE_SERVER_PORT', 6061))
        self.badge_interface: str = str(os.getenv('BADGE_SERVER_INTERFACE', '0.0.0.0'))
        self.badge_transport: str = str(os.getenv('BADGE_SERVER_TRANSPORT', 'tcp'))
        self.receipt_port: int = int(os.getenv('RECEIPT_SERVER_PORT', 6062))
        self.receipt_interface: str = str(os.getenv('RECEIPT_SERVER_INTERFACE', '0.0.0.0'))
        self.receipt_transport: str = str(os.getenv('RECEIPT_SERVER_TRANSPORT', 'tcp'))

    @property
    def frontend_connection_string(self):
        return f'{self.coordinator_transport}://{self.coordinator_interface}:{self.coordinator_port}'

    @property
    def badge_connection_string(self) -> str:
        return f'{self.badge_transport}://{self.badge_interface}:{self.badge_port}'

    @property
    def receipt_connetion_string(self) -> str:
        return f'{self.receipt_transport}://{self.receipt_interface}:{self.receipt_port}'