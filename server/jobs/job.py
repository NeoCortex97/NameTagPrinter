import json
import uuid
from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Self

from annotated_types import Ge, Gt

from jobs.exceptions import NoJobTypeError, NoMediaTypeError, NoMediaSizeError, NoJobDataError, InvalidJobTypeError, \
    InvalidMediaTypeError, InvalidMediaSizeError


class JobType(Enum):
    """ This enum describes the type of job.

    INVALID should be used while the job is not currently valid. invalid jobs should be ignored.

    DUMMY jobs are not used productively, but can be used for manual testing.

    RAW Jobs should not be used outside of display jobs.

    RASTER jobs contain raster data and are supposed to be not processed before being passed to the driver

    TEMPLATE jobs are processed by the custom template processor and the resulting raster job will be passed to the driver.
    """
    RAW = 'raw'
    DUMMY = 'dummy'
    RASTER = 'raster'
    INVALID = 'invalid'
    TEMPLATE = 'template'

    @classmethod
    def from_string(cls, value):
        return cls(value)


class Media(Enum):
    """ This Enum describes the media type to be used in the job.

    DUMMY media is not meant to produce a physical output. it is only used for testing of the job server.

    INVALID is used while no valid media is set. Invalid media jobs are supposed to be ignored.

    PAPER_LABEL is used if the job is to be processed by a paper label printer.

    RIBBON_LABEL is used if the job should be processed by a laminated ribbon label printer.

    TEXT_DISPLAY is used if the job is to be displayed by a user facing display.

    PAPER_RECEIPT is used if the job should be processed by a thermal receipt printer.

    GRAPHICS_DISPLAY is used if the job should be processed by a graphics capable user facing display.
    """
    DUMMY = 'dummy'
    INVALID = 'invalid'
    PAPER_LABEL = 'paperLabel'
    RIBBON_LABEL = 'ribbonLabel'
    TEXT_DISPLAY = 'textDisplay'
    PAPER_RECEIPT = 'paperReceipt'
    GRAPHICS_DISPLAY = 'graphicsDisplay'

    @classmethod
    def from_string(cls, value):
        return cls(value)


class JobStatus(Enum):
    """ This Enum describes the job states that can exist.

    A job is QUEUED if it is inside either the raw or processed job queue.

    A job is ABORTED if it is removed from the cups and processed job queue. or the cups job failed.

    A job is REMOVED if it is removed from the raw jab queue.

    A job is ABORTING if abortion of the job is in progress if the job is waiting to be removed from the cups and processed job queue.

    A job is CANCELED if it is removed from the raw queue without ever getting processed.

    A job is PREPARED if it is processed into a raster job and waiting to be pushed to the processed job queue.

    A job is QUEUEING if it is waiting to be pushed into the raw job queue.

    A job is CANCELLING while a cancel command is processed.

    A job is COMPLETED if a job is complete and waiting to be removed.

    A job is PREPARING while it is processed into a raster job.

    A job is PROCESSING while it is being printed.

    A jon is INITIALIZED if it is initialized and inside the job server and waiting to be transmitted to the print server.

    A job is INITIALIZED if it is initialized, but not validated.
    """
    QUEUED = 'queued'
    ABORTED = 'aborted'
    REMOVED = 'removed'
    ABORTING = 'aborting'
    CANCELED = 'canceled'
    PREPARED = 'prepared'
    QUEUEING = 'queueing'
    COMPLETED = 'completed'
    PREPARING = 'preparing'
    CANCELLING = 'canceling'
    PROCESSING = 'processing'
    INITIALIZED = 'initialized'
    INITIALIZING = 'initializing'

    @classmethod
    def from_string(cls, value):
        return cls(value)


@dataclass
class MediaSize:
    width: Annotated[int, Gt(0)]
    height: Annotated[int, Gt(0)]


class Job(ABC):
    def __init__(self):
        self.jobType: JobType = JobType.INVALID
        self.media: Media = Media.DUMMY
        self.mediaSize: MediaSize = None
        self.id : uuid = uuid.uuid4()
        self.priority: Annotated[int, Ge(0)] = 10
        self.data = None
        self.status: JobStatus = JobStatus.INITIALIZING
        self.rotation: int = 0
        self.copies: Annotated[int, Ge(1)] = 1

    @classmethod
    def parse(cls, message: str) -> Self:
        job = Job()

        data = json.loads(message)

        if 'type' not in data.keys():
            raise NoJobTypeError()
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
        job.data = data['data']
        job.status = JobStatus.from_string(data['status'])

        job.validate()

        return job

    def validate(self):
        if self.jobType == JobType.INVALID:
            raise InvalidJobTypeError()
        if self.media == Media.INVALID:
            raise InvalidMediaTypeError()
        if self.mediaSize.width <= 0 or self.mediaSize.height <= 0:
            raise InvalidMediaSizeError()