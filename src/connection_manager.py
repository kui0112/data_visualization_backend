import json
import threading
from typing import List

from starlette.websockets import WebSocket

from log import logger_factory

logger = logger_factory.get_logger(__name__)


class Connection:
    def __init__(self, ws: WebSocket):
        self.ws = ws
        self.active = True

    async def accept(self):
        await self.ws.accept()

    async def send(self, message: str):
        await self.ws.send_text(message)

    async def receive(self):
        return await self.ws.receive_text()

    async def close(self):
        self.active = False
        try:
            await self.ws.close()
        except Exception as ex:
            logger.debug(ex)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[Connection] = []
        self._lock = threading.Lock()

    async def connect(self, conn: Connection):
        await conn.accept()
        with self._lock:
            self.active_connections.append(conn)

    async def disconnect(self, conn: Connection):
        with self._lock:
            if conn in self.active_connections:
                await conn.close()
                self.active_connections.remove(conn)

    async def publish(self, message: str):
        for conn in self.active_connections:
            try:
                await conn.send(message)
            except Exception as ex:
                logger.debug(ex)
                await self.disconnect(conn)
