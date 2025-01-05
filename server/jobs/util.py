import base64
import json
import uuid

from jobs.exceptions import NoJobTypeError, NoJobDataError, NoMediaSizeError, NoMediaTypeError
from jobs.job import JobType, Media, MediaSize, JobStatus
from jobs.rasterJob import RasterJob


jobs = {
    JobType.RASTER: RasterJob
}


def parse_job(message: str) -> RasterJob:
    data: dict = json.loads(message)

    if 'type' not in data.keys():
        raise NoJobTypeError()

    job = jobs[JobType.from_string(data['type'])]()

    if 'media' not in data.keys():
        raise NoMediaTypeError()
    if 'size' not in data.keys():
        raise NoMediaSizeError()
    if 'data' not in data.keys():
        raise NoJobDataError()

    job.jobType = JobType.from_string(data['type'])
    job.media = Media.from_string(data['media'])
    job.mediaSize = MediaSize(data['size']['width'], data['size']['height'])
    if 'priority' in data.keys():
        job.priority = data['priority']
    job.data = base64.decodebytes(data['data'])
    job.status = JobStatus.from_string(data['status'])
    if 'id' in data.keys():
        job.id = uuid.UUID(hex=data['id'])

    job.validate()
    if job.status == JobStatus.INITIALIZING:
        job.status = JobStatus.INITIALIZED

    return job