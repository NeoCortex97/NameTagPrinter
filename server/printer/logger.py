import uuid
from tempfile import mktemp

import qrcode
from escpos.printer import Usb

name = 'NeoCortex97'
space = 'FlipDot'

""" Seiko Epson Corp. Receipt Printer (EPSON TM-T88III) """
p = Usb(0x04b8, 0x0202, 0, profile="TM-T88III")

p.image('../../assets/images/receipt/flipdot.png', center=True)
p.text('\n\n\n')

p.textln(f'Space:\t{space}\n')
p.textln(f'\tName:\t{name}')


id = str(uuid.uuid4())
code = qrcode.make(id)
temppath = mktemp(prefix='code')
code.save(temppath)

p.image(temppath, center=True)
p.textln(f'ID: {id}')

p.cut(mode='PART')