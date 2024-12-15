from PIL import ImageFont, ImageDraw
from brother_ql import BrotherQLRaster
from brother_ql.backends.helpers import send
from brother_ql.conversion import convert
from brother_ql.devicedependent import models, label_type_specs
from PIL import Image
import qrcode


PRINTER_MODEL = models[11]
LABEL_HEIGHT = label_type_specs['62']['dots_printable'][0]
SCALING_FACTOR = 2
font: ImageFont = ImageFont.truetype('../../../backend/assets/fonts/JetBrainsMono.ttf', 200)


image = Image.new('RGBA', (1200, LABEL_HEIGHT), (255, 255, 255))
logo = Image.open('../../../backend/assets/images/flipdot.png')
logo = logo.resize((int(logo.size[0] / SCALING_FACTOR), int(logo.size[1] / SCALING_FACTOR)))
logo.convert(mode='RGBA')


code: Image = qrcode.make('https://flipdot.org/').get_image()

name = 'NeoCortex'
name_img = Image.new('RGB', font.getbbox(name)[2:], color=(255, 255, 255))
name_draw = ImageDraw.Draw(name_img)
name_draw.text((0,0), name, font=font, fill=0)

image.paste(logo, (30, 35), logo)
image.paste(code, (image.size[0] - code.size[0], 0))
image.paste(name_img, (35, LABEL_HEIGHT - (name_img.size[1]  + 100)))
image.rotate(-90, expand=True)

qlr = BrotherQLRaster(PRINTER_MODEL)

instructions = convert(
        qlr=qlr,
        images=[image],
        label='62',
        rotate='90',    # 'Auto', '0', '90', '270'
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
