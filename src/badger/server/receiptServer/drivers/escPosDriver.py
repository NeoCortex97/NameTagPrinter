import pathlib
from tempfile import mktemp

import qrcode
from escpos.printer import Usb

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent
ASSET_ROOT = PROJECT_ROOT.joinpath('assets')


class ReceiptDriver:
    def __init__(self):
        self.printer = Usb(0x04b8, 0x0202, 0, profile="TM-T88III")

    def print(self, name, space, logo, url):
        self.printer.image(ASSET_ROOT.joinpath('images/receipt/flipdot.png'), center=True)
        self.printer.text('\n\n\n')

        self.printer.textln(f'Space:\t{space}\n')
        self.printer.textln(f'\tName:\t{name}')

        code = qrcode.make(f'{name};{space};{logo};{url};true')
        temppath = mktemp(prefix='code')
        code.save(temppath)

        self.printer.image(temppath, center=True)
        self.printer.cut(mode='PART')

    def process(self, job):
        self.print(job.name, job.space, job.logo, job.url)