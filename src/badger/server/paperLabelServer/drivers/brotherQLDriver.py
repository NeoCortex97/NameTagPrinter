import pathlib
from pprint import pprint
from tempfile import mktemp
from time import sleep

import cups
import qrcode
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from brother_ql import BrotherQLRaster
from brother_ql.devicedependent import models

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent
ASSET_ROOT = PROJECT_ROOT.joinpath('assets')
FONT_FOLDER = ASSET_ROOT.joinpath('fonts')
LOGO_PATH = ASSET_ROOT .joinpath('images/logos')

class BrotherQLDriver:
    def __init__(self):
        self.PRINTER_NAME = 'Brother_QL_820NWB_USB'
        self.LABEL_HEIGHT = 696
        self.SCALING_FACTOR = 2.5
        self.LOGO_THRESHOLD = 10
        self.conn = cups.Connection()
        self.font_path = FONT_FOLDER.joinpath('JetBrainsMono.ttf')
        self.max_font_size = 200
        self.label_width = 1200
        self.name_margin = 20

        PRINTER_MODEL = models[11]

        self.printer =  BrotherQLRaster(PRINTER_MODEL)

    def print(self, name: str, space: str, logo: str, url: str):

        image = self.generate_image(name, space, logo, url)

        # instructions = convert(
        #     qlr=self.drivers,
        #     images=[image],
        #     label='62',
        #     rotate='0',  # 'Auto', '0', '90', '270'
        #     threshold=70.0,  # Black and white threshold in percent.
        #     dither=False,
        #     compress=False,
        #     dpi_600=True,
        #     hq=True,
        #     cut=True
        # )
        #
        # send(
        #     instructions=instructions,
        #     printer_identifier='usb://0x04f9:0x209d',
        #     backend_identifier='pyusb',
        #     blocking=True
        # )

        image.show('debug')

        outfile = mktemp(prefix='png')
        image.save(outfile, 'png')

        job_id = self.conn.printFile(self.PRINTER_NAME, outfile, f'Badge {name}', {
            'print-scaling': 'fill',
            'PageSize': 'Custom.62x109mm',
            'ColorModel': 'AutoGray',
            'MediaType': 'Roll',
            'CutMedia': 'Auto',
        })

        pprint(self.conn.getJobAttributes(job_id))

        self.wait_for_jobs(job_id)

    def generate_image(self, name, space, logo, url):
        image = Image.new('RGBA', (self.label_width, self.LABEL_HEIGHT), (255, 255, 255))

        logo_image = self.process_logo(space, logo)
        # logo_image.show("debug")
        image.paste(logo_image, (30, 33), logo_image)

        font_size = self.max_font_size
        while ImageFont.truetype(str(self.font_path), font_size).getbbox(name)[2] > self.label_width - (
                2 * self.name_margin):
            font_size -= 1
        font = ImageFont.truetype(str(self.font_path), font_size)
        name_img = Image.new('RGB', font.getbbox(name)[2:], color=(255, 255, 255))
        name_draw = ImageDraw.Draw(name_img)
        name_draw.text((0, 0), name, font=font, fill=0)
        image.paste(name_img, (35, self.LABEL_HEIGHT - (name_img.size[1] + 100)))

        if url is not None and url.strip() != '':
            code: Image = qrcode.make(url).get_image()
            image.paste(code, (image.size[0] - code.size[0], 0))

        image = image.rotate(-90, expand=True)
        # image = image.convert('L')
        return image

    def process_logo(self, space: str, logo: str or pathlib.Path):
        if type(logo) == str and logo is not None and logo.strip() != '' and LOGO_PATH.joinpath(logo).exists():
            path = LOGO_PATH.joinpath(logo)
            logo_image = Image.open(path).convert('RGBA')
            logo_image = logo_image.resize((int(logo_image.size[0] / self.SCALING_FACTOR), int(logo_image.size[1] / self.SCALING_FACTOR)))
            # logo_image = logo_image.convert('LA')
            logo_image = logo_image.point(lambda p : 255 if p > self.LOGO_THRESHOLD else 0)
            logo_image.rotate(-90, expand=True)
            return logo_image
        elif type(logo) == str and space is not None and space.strip() != '':
            tmp_font = ImageFont.truetype(str(self.font_path), 100)
            logo_image = Image.new('RGBA', tmp_font.getbbox(space)[2:], color=(255, 255, 255, 0))
            logo_draw = ImageDraw.Draw(logo_image)
            logo_draw.text((0, 0), space, font=tmp_font, fill=(0, 0, 0, 255))
            return logo_image
        elif type(logo) == pathlib.PosixPath:
            logo_image = Image.open(logo)
            height_factor = logo_image.size[1] / (self.LABEL_HEIGHT / 2.1)
            width_factor = logo_image.size[1] / (self.label_width / 3)
            scaling_factor = max(height_factor, width_factor)
            logo_image = logo_image.resize((int(logo_image.size[0]/scaling_factor), int(logo_image.size[1] / scaling_factor)))
            logo_image = logo_image.convert('RGBA')
            print(logo_image.size)
            return logo_image

    def wait_for_jobs(self, job_id):
        jobs: dict = self.conn.getJobs()
        while job_id in jobs.keys():
            sleep(0.25)
            jobs = self.conn.getJobs()

    def process(self, job):
        self.print(job.name, job.space, job.logo, job.url)
