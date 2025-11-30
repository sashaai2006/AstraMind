from __future__ import annotations

import asyncio
import json
from typing import Dict, Set

from fastapi import WebSocket


class WSManager:
    """Track WebSocket connections per project."""

    def __init__(self) -> None:
        self._connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, project_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.setdefault(project_id, set()).add(websocket)

    async def disconnect(self, project_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            conns = self._connections.get(project_id)
            if not conns:
                return
            conns.discard(websocket)
            if not conns:
                self._connections.pop(project_id, None)

    async def broadcast(self, project_id: str, payload: Dict[str, str]) -> None:
        async with self._lock:
            connections = list(self._connections.get(project_id, set()))

        message = json.dumps(payload, default=str)
        for connection in connections:
            await connection.send_text(message)


ws_manager = WSManager()

