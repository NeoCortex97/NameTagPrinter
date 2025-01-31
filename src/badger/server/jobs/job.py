import base64
import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from annotated_types import Ge, Gt

from badger.server.jobs.exceptions import InvalidMediaSizeError, InvalidJobTypeError, InvalidMediaTypeError, \
    InvalidRotationError, InvalidPriorityError, InvalidNumberOfCopiesError


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
    SCRIPT = 'script'
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
    """ This class describes the Media to be used.

    width and height are in relation to the way the medium is oriented in thw printer.\n

    :param width: Represents the width of the medium.
    :type width: int greater than 0
    :param height: Represents the height of the medium.
    :type height: int greater than 0
    """
    width: Annotated[int, Gt(0)]
    height: Annotated[int, Gt(0)]

    def validate(self):
        if self.width <= 0 or self.height <= 0:
            raise InvalidMediaSizeError()

    def __repr__(self):
        return f'{self.width}x{self.height}'


class Job(ABC):
    """ A generic representation of a print job.

    """
    def __init__(self):
        self.jobType: JobType = JobType.INVALID
        self.media: Media = Media.DUMMY
        self.mediaSize: MediaSize = MediaSize(0, 0)
        self.id : uuid = uuid.uuid4()
        self.priority: Annotated[int, Ge(0)] = 10
        self.status: JobStatus = JobStatus.INITIALIZING
        self.rotation: int = 0
        self._data = None
        self.copies: Annotated[int, Ge(1)] = 1

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    def validate(self):
        """ Verifies the loaded data is valid.
        In an ideal world this should allways return true.
        If it raises an exception, you should forward te exception to your client and dop the job.

        :return: Nothing.
        :raise: InvalidJobTypeError if the JobType has the Value INVALID.
                Invalid jobs should never be transmitted through a socket. It is only used if the jo is not yet fully constructed.
        :raise: InvalidMediaTypeError if the media type is not supported.
        :raise: InvalidRotationError
        :raise: InvalidPriorityError
        :raise: InvalidNumberOfCopiesError
        """
        if self.jobType == JobType.INVALID:
            raise InvalidJobTypeError()
        if self.media == Media.INVALID:
            raise InvalidMediaTypeError()
        self.mediaSize.validate()
        if self.rotation not in [0, 90, 180, 270]:
            raise InvalidRotationError()
        if self.priority <= 0:
            raise  InvalidPriorityError()
        if self.copies < 1:
            raise InvalidNumberOfCopiesError()

    def to_json(self) -> str:
        """ Serializes the job into a json encoded string.

        :return: string
        """
        return json.dumps({
            'id': self.id.hex,
            'type': self.jobType.value,
            'media': self.media.value,
            'size': {'width': self.mediaSize.width, 'height': self.mediaSize.height},
            'priority': self.priority,
            'status': self.status.value,
            'copies': self.copies,
            'data': base64.b64encode(self.get_data_bytes()).decode('utf-8')
        })

    def __repr__(self):
        return f'{self.id} {self.jobType} - {self.copies}x {self.media}({self.mediaSize})'

    @abstractmethod
    def get_data_bytes(self) -> bytes:
        pass

