from abc import ABC, abstractmethod

from jobs.job import Job


class JobProcessor(ABC):
    @abstractmethod
    def is_applicable(self, job: Job) -> bool: ...
    @abstractmethod
    def apply(self, job): ...
