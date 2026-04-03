class MemoryStore:
    def __init__(self):
        self._data = {}

    def set(self, key: str, value: any):
        self._data[key] = value

    def get(self, key: str):
        return self._data.get(key)

db = MemoryStore()
