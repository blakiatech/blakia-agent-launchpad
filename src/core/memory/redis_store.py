# core/memory/redis_store.py
"""Almacenamiento de ventana de conversación en Redis."""

from __future__ import annotations

from typing import List, cast
from redis import Redis
from pydantic_ai.messages import ModelMessage
from .manager import HistoryStore
from .codec import dumps_list, loads_list

__all__ = ["RedisWindowStore"]


class RedisWindowStore(HistoryStore):
    """Persistencia sencilla de mensajes usando Redis (un JSON por item)."""

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    def get(self, session_id: str) -> List[ModelMessage]:
        raw = cast("list[str | bytes]", self.redis_client.lrange(session_id, 0, -1))
        return loads_list(raw)

    def set(self, session_id: str, messages: List[ModelMessage]) -> None:
        self.redis_client.delete(session_id)
        payloads = dumps_list(messages)
        if payloads:
            self.redis_client.rpush(session_id, *payloads)

    def clear(self, session_id: str) -> None:
        self.redis_client.delete(session_id)
