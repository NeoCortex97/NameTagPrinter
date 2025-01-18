from badger.server.jobs.job import Job


class DummyJob(Job):
    def get_data_bytes(self) -> bytes:
        pass