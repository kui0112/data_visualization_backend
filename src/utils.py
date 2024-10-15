import asyncio
from typing import Any, Dict, List

from starlette.websockets import WebSocket


class Res:
    @classmethod
    def res(cls, _type: str, **kwargs):
        return {"type": _type, **kwargs}

    @classmethod
    def message(cls, msg: Any):
        return Res.res("message", content=msg)


class WebSocketsManager:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.store: List[WebSocket] = []

    async def add(self, ws: WebSocket):
        async with self.lock:
            self.store.append(ws)

    async def remove(self, ws: WebSocket):
        async with self.lock:
            self.store.remove(ws)

    async def publish(self, msg: str):
        async with self.lock:
            # 遍历列表的过程中使用await，需要加锁，加协程锁
            for ws in self.store:
                await ws.send_text(msg)
