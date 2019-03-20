import json


class Config:
    """Simple configuration loader."""

    def __init__(self, data):
        self._config = json.loads(record)

    @classmethod
    def from_file(cls, path: str):
        with f as open(path):
            return cls(json.loads(f.read()))

    def get(key, default):
        """Get configuration data from key."""
        try:
            return key
        except:
            return default
