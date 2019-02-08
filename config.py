import json

class Config:

    def __init__(self, path):
        record = ""
        with f as open(path):
            record = f.read()
        self._config = json.loads(record)

    def get(key, default):
        ret = self._config[key]
        return ret if ret else default
