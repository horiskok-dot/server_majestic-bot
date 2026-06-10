from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class WebSocketManager:
    def __init__(self) -> None:
        self._channels: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, channel: str, websocket: WebSocket, accept: bool = True) -> None:
        if accept:
            await websocket.accept()
        self._channels[channel].add(websocket)

    def disconnect(self, channel: str, websocket: WebSocket) -> None:
        self._channels[channel].discard(websocket)

    async def broadcast(self, channel: str, event: str, payload: dict[str, Any]) -> None:
        dead: list[WebSocket] = []
        message = {"event": event, "payload": payload}
        agent_id = payload.get("agent_id")
        
        for websocket in list(self._channels[channel]):
            user_id = getattr(websocket.state, "user_id", None)
            if user_id is not None and agent_id:
                from ..database import SessionLocal
                from ..models import Agent
                with SessionLocal() as db:
                    agent = db.query(Agent).filter(Agent.agent_id == agent_id, Agent.user_id == user_id).first()
                    if not agent:
                        continue
            try:
                await websocket.send_json(message)
            except Exception:
                dead.append(websocket)
        for websocket in dead:
            self.disconnect(channel, websocket)


ws_manager = WebSocketManager()
