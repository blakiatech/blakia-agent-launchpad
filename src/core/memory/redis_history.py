# core/memory/redis_history.py
from __future__ import annotations
from typing import List, cast
import redis

from pydantic_ai.messages import ModelMessage
from .manager import HistoryStore
from .codec import dumps_list, loads_list, attach_model_dump_json_shim

# Garantiza compatibilidad con tests que usan .model_dump_json()
attach_model_dump_json_shim()


class RedisHistory(HistoryStore):
    """
    Historial por sesión en Redis usando lista (un JSON por item).
    Implementa HistoryStore (get/set/clear) y expone _load/_save como compat.
    """

    def __init__(self, session_id: str, redis_client: redis.Redis):
        self.session_id = session_id
        self.redis_client = redis_client

    # --- Interfaz HistoryStore ---
    def get(self, sid: str) -> List[ModelMessage]:
        if sid != self.session_id:
            # historial atado a un session_id concreto
            return []
        raw = cast(
            "list[str | bytes]", self.redis_client.lrange(self.session_id, 0, -1)
        )
        return loads_list(raw)

    def set(self, sid: str, messages: List[ModelMessage]) -> None:
        if sid != self.session_id:
            return
        self.redis_client.delete(self.session_id)
        payloads = dumps_list(messages)
        if payloads:
            self.redis_client.rpush(self.session_id, *payloads)

    def clear(self, sid: str) -> None:
        if sid != self.session_id:
            return
        self.redis_client.delete(self.session_id)

    # --- Compatibilidad con el código/tests existentes ---
    def _load(self) -> List[ModelMessage]:
        return self.get(self.session_id)

    def _save(self, messages: List[ModelMessage]) -> None:
        self.set(self.session_id, messages)
