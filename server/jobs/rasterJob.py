import io

from PIL import Image

from jobs.job import Job


class RasterJob(Job):
    def __init__(self):
        super().__init__()
        self._data: Image = None

    @Job.data.setter
    def data(self, data):
        self._data = Image.open(io.BytesIO(data))

    @Job.data.getter
    def data(self) -> Image.Image:
        return self._data

