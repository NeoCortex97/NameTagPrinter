import os
import pathlib
from tempfile import mktemp
from time import sleep

import cups
import qrcode
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


FONT_FOLDER = pathlib.Path('../assets/fonts/')
LOGO_PATH = pathlib.Path('../assets/images/logos')

class BadgeDriver:
    def __init__(self):
        self.PRINTER_NAME = 'Brother_QL_820NWB'
        self.LABEL_HEIGHT = 696
        self.SCALING_FACTOR = 2.5
        self.LOGO_THRESHOLD = 10
        self.conn = cups.Connection()
        self.font_path = FONT_FOLDER.joinpath('JetBrainsMono.ttf')
        self.max_font_size = 200
        self.label_width = 1200
        self.name_margin = 20

    def print(self, name: str, space: str, logo: str, url: str):

        image = Image.new('RGBA', (self.label_width, self.LABEL_HEIGHT), (255, 255, 255))

        logo_image = self.process_logo(space, logo)
        logo_image.show("debug")
        image.paste(logo_image, (30, 33), logo_image)

        font_size = self.max_font_size
        while ImageFont.truetype(self.font_path, font_size).getbbox(name)[2] > self.label_width - (2 * self.name_margin):
            font_size -= 1
        font = ImageFont.truetype(self.font_path, font_size)
        name_img = Image.new('RGB', font.getbbox(name)[2:], color=(255, 255, 255))
        name_draw = ImageDraw.Draw(name_img)
        name_draw.text((0, 0), name, font=font, fill=0)
        image.paste(name_img, (35, self.LABEL_HEIGHT - (name_img.size[1] + 100)))

        if url is not None and url.strip() != '':
            code: Image = qrcode.make(url).get_image()
            image.paste(code, (image.size[0] - code.size[0], 0))

        image.rotate(-90, expand=True)
        image = image.convert('1')

        outfile = mktemp(prefix='png')
        image.save(outfile, 'png')

        self.conn.printFile(self.PRINTER_NAME, outfile, f'Badge {name}', {
            'print-scaling': 'fill',
            'PageSize': 'Custom.62x109mm',
            'MediaType': 'Roll',
            'CutMedia': 'Auto',
            'ColorModel': 'AutoGray'
        })

        self.wait_for_jobs()



    def process_logo(self, space: str, logo: str):
        if logo is not None and logo.strip() != '':
            path = LOGO_PATH.joinpath(logo)
            logo_image = Image.open(path).convert('RGBA')
            logo_image = logo_image.resize((int(logo_image.size[0] / self.SCALING_FACTOR), int(logo_image.size[1] / self.SCALING_FACTOR)))
            logo_image = logo_image.convert('LA')
            logo_image = logo_image.point(lambda p : 255 if p > self.LOGO_THRESHOLD else 0)
            logo_image.rotate(-90, expand=True)
            return logo_image
        elif space is not None and space.strip() != '':
            tmp_font = ImageFont.truetype(self.font_path, 100)
            logo_image = Image.new('RGBA', tmp_font.getbbox(space)[2:], color=(255, 255, 255, 0))
            logo_draw = ImageDraw.Draw(logo_image)
            logo_draw.text((0, 0), space, font=tmp_font, fill=(0, 0, 0, 255))
            return logo_image

    def wait_for_jobs(self):
        jobs: dict = self.conn.getJobs()
        while len(jobs.keys()) > 0:
            sleep(0.25)
            jobs = self.conn.getJobs()