from abc import ABC, abstractmethod
from typing import Iterable, Type

from badger.server.jobs.job import Job


class JobProcessor(ABC):
    @abstractmethod
    def is_applicable(self, job: Job) -> bool: ...
    @abstractmethod
    def apply(self, job): ...


def get_processors() -> list[Type[JobProcessor]]:
    return JobProcessor.__subclasses__()
