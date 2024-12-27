import os
import pathlib

import dotenv
from appdirs import AppDirs


class LabelConfig:
    def __init__(self):
        self.width = int(os.getenv('LABEL_WIDTH', 62))
        self.height = int(os.getenv('LABEL_HEIGHT', 109))
        self.dpi: int = int(os.getenv('LABEL_DPI', 300))

    @property
    def resolution(self) -> tuple[int, int]:
        return int(self.dpi * (self.width / 25.4)), int(self.dpi * (self.height / 25.4))


class PrinterConfig:
    def __init__(self):
        self.model: str = str(os.getenv('BADGE_PRINTER_MODEL', 'Brother_QL_820NWB_USB'))
        self.label: LabelConfig = LabelConfig()
        self.print_options: dict[str, str] = {
            'print-scaling': os.getenv('BADGE_PRINTER_SCALING', 'fill'),
            'PageSize': f'Custom.{self.label.width}x{self.label.height}mm',
            'MediaType': os.getenv('BADGE_PRINTER_MEDIA', 'Roll'),
            'media': f'Custom.{self.label.width}x{self.label.height}mm',
            'CutMedia': os.getenv('BADGE_PRINTER_CUT', 'Auto')
        }


class BadgeConfig:
    PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent # TODO: Deprecate this hacky solution
    def __init__(self):
        dirs = AppDirs('NameTagger')
        config_roots = [pathlib.Path(p) for p in set(':'.join([str(self.PROJECT_ROOT), os.getcwd(), dirs.user_config_dir, dirs.site_config_dir]).split(':'))]
        asset_roots = [path.joinpath(os.getenv('BADGE_SERVER_ASSET_ROOT', 'assets')) for path in config_roots]
        print(config_roots)
        print(asset_roots)

        self.font_paths: list[pathlib.Path] = [path.joinpath(os.getenv('BADGE_SERVER_FONT_PATH', 'fonts')) for path in asset_roots]
        self.logo_paths: list[pathlib.Path] = [path.joinpath(os.getenv('BADGE_SERVER_LOGO_PATH', 'logos')) for path in asset_roots]

        self.max_font_size: int = int(os.getenv('BADGE_PRINTER_MAX_FONT_SIZE', 200))
        self.name_margin: int = int(os.getenv('BADGE_NAME_MARGIN', 20))
        self.logo_margin: int = int(os.getenv('BADGE_LOGO_MARGIN', 30))
        self.qr_margin: int = int(os.getenv('BADGE_QR_MARGIN', 0))
        self.default_font: str = str(os.getenv('BADGE_DEFAULT_FONT', 'JetBrainsMono'))
        self.default_logo: str = str(os.getenv('BADGE_DEFAULT_LOGO', 'c3'))

    @property
    def fonts(self) -> dict[str, pathlib.Path]:
        result = {}
        for path in [p for p in self.font_paths if p.exists()]:
            for file in [ p for p in path.iterdir() if p.is_file() and p.suffix == '.ttf']:
                result[file.stem.replace('.ttf', '')] = file
        return result

    @property
    def font (self):
        return self.fonts[self.default_font]

    @property
    def logos(self) -> dict[str, pathlib.Path]:
        result = {}
        for  path in [p for p in self.logo_paths if p.exists()]:
            for file in [p for p in path.iterdir() if p.is_file() and p.suffix == '.png']:
                result[file.stem.replace('.png', '')] = file
        return result


class BadgeServerConfig:
    def __init__(self):
        dotenv.load_dotenv()

        self.port: int = int(os.getenv('BADGE_SERVER_PORT', 6061))
        self.interface: str = str(os.getenv('BADGE_SERVER_INTERFACE', '127.0.0.1'))
        self.transport: str = str(os.getenv('BADGE_SERVER_TRANSPORT', 'tcp'))
        self.queue_size: int = int(os.getenv('BADGE_SERVER_QUEUE_SIZE', 16))
        self.timeout: int = int(os.getenv('BADGE_SERVER_QUEUE_TIMEOUT', 2))

        self.printer: PrinterConfig = PrinterConfig()

        self.badge: BadgeConfig = BadgeConfig()

    @property
    def connection_string(self) -> str:
        return f'{self.transport}://{self.interface}:{self.port}'
