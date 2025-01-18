from typing import Tuple

from badger.server.jobs.job import Job, JobType
from badger.server.jobs.rasterJob import RasterJob
from badger.server.jobs.jobProcessor import JobProcessor


class RasterProcessor(JobProcessor):
    def is_applicable(self, job: Job) ->  bool:
        """
        :param job:
        :return: True if the processor can process this job.
        """
        return job.jobType == JobType.RASTER

    def apply(self, job: RasterJob) -> Tuple[Job or None, Job or None]:
        """ Applies transformations from one job type to another.
        If the job is not directly printable it will be returned as the first element, so it can be placed into the job queue.
        If the element is returned as the second element it is o be placed into the work queue for printing.

        :param job:
        :return:
        """
        return None, job