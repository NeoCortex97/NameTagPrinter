import base64
import io

from PIL import Image

from jobs.job import Job


class RasterJob(Job):
    def __init__(self):
        super().__init__()
        self._data: Image = Image.Image()

    @Job.data.setter
    def data(self, data):
        self._data = Image.open(io.BytesIO(data))

    @Job.data.getter
    def data(self) -> Image.Image:
        return self._data

    def get_data_bytes(self) -> bytes:
        buffer = io.BytesIO()
        self.data.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue())
