from badger.server.jobs.job import Job, JobType
from badger.server.jobs.jobProcessor import JobProcessor


class ScriptProcessor(JobProcessor):
    def is_applicable(self, job: Job) -> bool:
        return job.jobType == JobType.SCRIPT

    def apply(self, job):
        pass