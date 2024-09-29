import json
from typing import Any


class Res:
    @classmethod
    def res(cls, _type: str, **kwargs):
        return {"type": _type, **kwargs}

    @classmethod
    def message(cls, msg: Any):
        return Res.res("message", content=msg)

    @classmethod
    def command(cls, operation: str, **args):
        return Res.res("command", operation=operation, **args)

    @classmethod
    def update(cls, **kwargs):
        return cls.command("update", **kwargs)

    @classmethod
    def heartbeat(cls):
        return cls.res("heartbeat")
