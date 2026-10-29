"""In-memory KV storage."""
import time

class StorageEngine:
    def __init__(self):
        self._data = {}
        self._expiry = {}

    def set(self, key: str, value: str, ttl: int = 0):
        self._data[key] = value
        if ttl > 0:
            self._expiry[key] = time.time() + ttl

    def get(self, key: str) -> str:
        if key in self._expiry and time.time() > self._expiry[key]:
            del self._data[key]
            del self._expiry[key]
            return None
        return self._data.get(key)
