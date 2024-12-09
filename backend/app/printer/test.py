from brother_ql import BrotherQLRaster
from brother_ql.backends.helpers import send
from brother_ql.conversion import convert
from brother_ql.devicedependent import models, label_type_specs
from PIL import Image


PRINTER_MODEL = models[11]
LABEL_HEIGHT = label_type_specs['62']['dots_printable'][0]
SCALING_FACTOR = 3

image = Image.new('RGBA', (LABEL_HEIGHT, 500), (255, 255, 255))
logo = Image.open('../../assets/images/flipdot.png')
logo = logo.resize((logo.size[0] // SCALING_FACTOR, logo.size[1] // SCALING_FACTOR))
logo.convert(mode='RGBA')
# logo = logo.rotate(-90, expand=True)
image.paste(logo, (int((LABEL_HEIGHT - logo.size[0]) / 2.0), 20), logo)

qlr = BrotherQLRaster(PRINTER_MODEL)

instructions = convert(
        qlr=qlr,
        images=[image],
        label='62',
        rotate='auto',    # 'Auto', '0', '90', '270'
        threshold=70.0,    # Black and white threshold in percent.
        dither=False,
        compress=False,
        dpi_600=False,
        hq=True,
        cut=True
)

send(
    instructions=instructions,
    printer_identifier='usb://0x04f9:0x209d',
    backend_identifier='pyusb',
    blocking=True
)
