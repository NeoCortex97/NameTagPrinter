from time import sleep

import brother_label.labels
import cups

from PIL import ImageFont, ImageDraw
from PIL import Image
from tempfile import mktemp
import qrcode


PRINTER_NAME = 'Brother_QL_820NWB'
LABEL_HEIGHT = 696
SCALING_FACTOR = 2.5
LOGO_THRESHOLD = 10
font: ImageFont = ImageFont.truetype('../../../backend/assets/fonts/JetBrainsMono.ttf', 200)


image = Image.new('RGBA', (1200, LABEL_HEIGHT), (255, 255, 255))
logo = Image.open('../../assets/images/test/flipdot2.png').convert('RGBA')
logo = logo.resize((int(logo.size[0] / SCALING_FACTOR), int(logo.size[1] / SCALING_FACTOR)))
# logo = logo.convert('LA')
# logo = logo.point(lambda p : 255 if p > LOGO_THRESHOLD else 0)
logo.rotate(-90, expand=True)

code: Image = qrcode.make('https://flipdot.org/').get_image()

name = 'NeoCortex'
name_img = Image.new('RGB', font.getbbox(name)[2:], color=(255, 255, 255))
name_draw = ImageDraw.Draw(name_img)
name_draw.text((0,0), name, font=font, fill=0)

image.paste(logo, (30, 33), logo)
image.paste(code, (image.size[0] - code.size[0], 0))
image.paste(name_img, (35, LABEL_HEIGHT - (name_img.size[1]  + 100)))
image.rotate(-90, expand=True)
image = image.convert('1')

outfile = mktemp(prefix='png')
image.save(outfile, 'png')

# image.show('asdf')

conn = cups.Connection()
printers = conn.getPrinters()

conn.printFile(PRINTER_NAME, outfile, f'Badge {name}', {
    'print-scaling': 'fill',
    'PageSize': 'Custom.62x109mm',
    'MediaType': 'Roll',
    'CutMedia': 'Auto',
    'ColorModel': 'AutoGray'
})

jobs: dict = conn.getJobs()
print(jobs)

for job in jobs.keys():
    print(conn.getJobAttributes(job))

while len(jobs.keys()) > 0:
    sleep(0.25)
    jobs = conn.getJobs()

print()
