from badger.server.jobs.job import Job, JobType
from badger.server.jobs.jobProcessor import JobProcessor


class DummyProcessor(JobProcessor):
    def is_applicable(self, job: Job) -> bool:
        return job.jobType == JobType.DUMMY

    def apply(self, job):
        print(f'Discarding Job: {job}')
        return None, None