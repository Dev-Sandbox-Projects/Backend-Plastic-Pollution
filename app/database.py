import json

class MemoryStore:
    def __init__(self):
        self._data = {}

    def set(self, key: str, value: any):
        self._data[key] = value

    def get(self, key: str):
        return self._data.get(key)

    def dump_all(self) -> str:
        # Export data for debug
        try:
            return json.dumps(self._data, indent=4, ensure_ascii=False)
        except Exception:
            return str(self._data)

db = MemoryStore()
