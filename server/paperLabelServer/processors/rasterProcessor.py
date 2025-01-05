from typing import Tuple

from jobs.job import Job, JobType
from jobs.rasterJob import RasterJob
from processors.jobProcessor import JobProcessor


class RasterProcessor(JobProcessor):
    def is_applicable(self, job: Job) ->  bool:
        return job.jobType == JobType.RASTER

    def apply(self, job: RasterJob) -> Tuple[Job or None, Job or None]:
        return None, job