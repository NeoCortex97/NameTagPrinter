import pathlib
import uuid


class Job:
    def __init__(self, name: str, space: str = 'independent', logo: pathlib.Path = None, url: str = None, copies: int = 1):
        self.name = name
        self.space = space
        self.logo = logo
        self.url = url
        self.copies = copies
        self.id = uuid.uuid4()

    def __repr__(self):
        return f'[{self.id}] {self.space} -> {self.name} ({self.logo}, {self.url}) x{self.copies}'

