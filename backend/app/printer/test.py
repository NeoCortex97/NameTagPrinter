from PIL import ImageFont, ImageDraw
from brother_ql import BrotherQLRaster
from brother_ql.backends.helpers import send
from brother_ql.conversion import convert
from brother_ql.devicedependent import models, label_type_specs
from PIL import Image
import qrcode


PRINTER_MODEL = models[11]
LABEL_HEIGHT = label_type_specs['62']['dots_printable'][0]
SCALING_FACTOR = 2.5
font: ImageFont = ImageFont.truetype('../../../backend/assets/fonts/JetBrainsMono.ttf', 150)


image = Image.new('RGBA', (LABEL_HEIGHT, 1200), (255, 255, 255))
logo = Image.open('../../../backend/assets/images/flipdot.png')
logo = logo.resize((int(logo.size[0] / SCALING_FACTOR), int(logo.size[1] / SCALING_FACTOR)))
logo.convert(mode='RGBA')
logo = logo.rotate(-90, expand=True)

code: Image = qrcode.make('https://flipdot.org/').get_image()

name = 'NeoCortex'
name_img = Image.new('RGB', font.getbbox(name)[2:], color=(255, 255, 255))
name_draw = ImageDraw.Draw(name_img)
name_draw.text((0,0), name, font=font, fill=0)
name_img = name_img.rotate(-90, expand=True)

image.paste(logo, (int((LABEL_HEIGHT - logo.size[0]) / 1.2), 30), logo)
image.paste(code, (0, 0))
image.paste(name_img, (50, code.size[1] + 30))

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

send(
    instructions=instructions,
    printer_identifier='tcp://192.168.178.135',
    backend_identifier='network',
    blocking=True
)
