import os
import pathlib

import dotenv
from appdirs import AppDirs


class LogoNotFoundError(Exception):
    pass


class PrinterConfig:
    def __init__(self):
        pass

class ReceiptConfig:
    PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent  # TODO: Deprecate this hacky solution
    def __init__(self):
        dirs = AppDirs('NameTagger')
        config_roots = [pathlib.Path(p) for p in set(':'.join([str(self.PROJECT_ROOT), os.getcwd(), dirs.user_config_dir, dirs.site_config_dir]).split(':'))]
        self.asset_roots = [path.joinpath(os.getenv('RECEIPT_SERVER_ASSET_ROOT', 'assets')) for path in config_roots]
        self.logo_name: str = str(os.getenv('RECEIPT_LOGO_NAME', 'receipt/flipdot.png'))


    @property
    def logo(self) -> pathlib.Path:
        instances = [p for p in [path.joinpath(self.logo_name) for path in self.asset_roots] if p.exists()]
        if len(instances) == 0:
            raise LogoNotFoundError()
        return instances[0]


class ReceiptServerConfig:
    def __init__(self):
        dotenv.load_dotenv()

        self.port: int = int(os.getenv('RECEIPT_SERVER_PORT', 6062))
        self.interface: str = str(os.getenv('RECEIPT_SERVER_INTERFACE', '0.0.0.0'))
        self.transport: str = str(os.getenv('RECEIPT_SERVER_TRANSPORT', 'tcp'))
        self.queue_size: int = int(os.getenv('RECEIPT_SERVER_QUEUE_SIZE', 16))

        self.printer: PrinterConfig = PrinterConfig()

        self.receipt: ReceiptConfig = ReceiptConfig()

    @property
    def connection_string(self) -> str:
        return f'{self.transport}://{self.interface}:{self.port}'
