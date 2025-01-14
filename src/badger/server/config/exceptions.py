class NotAConfigSectionError(Exception):
    def __init__(self, section: str):
        super().__init__()
        self.section = section
        self.id = 1


class NotASettingError(Exception):
    def __init__(self, section: str, key: str, value: str = None):
        super().__init__()
        self.section = section
        self.setting = key
        self.value = value
        self.id = 2
