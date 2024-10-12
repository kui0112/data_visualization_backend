import threading
from typing import Any, Dict


class Res:
    @classmethod
    def res(cls, _type: str, **kwargs):
        return {"type": _type, **kwargs}

    @classmethod
    def message(cls, msg: Any):
        return Res.res("message", content=msg)


class ConcurrentDict:
    def __init__(self, init_values: Dict):
        self.lock = threading.Lock()
        self.store = init_values

    def get(self, key: str):
        with self.lock:
            return self.store.get(key)

    def set(self, key: str, value: Any):
        with self.lock:
            self.store[key] = value
