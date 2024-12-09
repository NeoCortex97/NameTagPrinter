from brother_ql import BrotherQLRaster
from brother_ql.backends.helpers import send
from brother_ql.conversion import convert
from brother_ql.devicedependent import models, label_type_specs
from PIL import Image
import qrcode


PRINTER_MODEL = models[11]
LABEL_HEIGHT = label_type_specs['62']['dots_printable'][0]
SCALING_FACTOR = 3

image = Image.new('RGBA', (LABEL_HEIGHT, 500), (255, 255, 255))
logo = Image.open('backend/assets/images/flipdot.png')
logo = logo.resize((logo.size[0] // SCALING_FACTOR, logo.size[1] // SCALING_FACTOR))
logo.convert(mode='RGBA')
# logo = logo.rotate(-90, expand=True)

code = qrcode.make('https://flipdot.org/')

image.paste(logo, (int((LABEL_HEIGHT - logo.size[0]) / 1.5), 20), logo)
image.paste(code, (int((logo.size[0]) / 1.5), 20))

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

image.show()

# send(
#     instructions=instructions,
#     printer_identifier='tcp://192.168.178.135',
#     backend_identifier='network',
#     blocking=True
# )
