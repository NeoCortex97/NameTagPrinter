from badger.server.jobs.job import Job
from badger.server.processors.jobProcessor import JobProcessor


class TemplateProcessor(JobProcessor):
    def is_applicable(self, job: Job) -> bool:
        pass

    def apply(self, job):
        pass