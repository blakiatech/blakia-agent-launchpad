# core/memory/manager.py
from __future__ import annotations
from typing import Protocol, List
from pydantic_ai.messages import ModelMessage
from core.memory.processors import strip_tool_traffic
from core.memory.processors import keep_recent_messages  # async


class HistoryStore(Protocol):
    def get(self, sid: str) -> List[ModelMessage]: ...
    def set(self, sid: str, messages: List[ModelMessage]) -> None: ...
    def clear(self, sid: str) -> None: ...


class MemoryManager:
    """Coordina acceso a una o varias stores de historial."""

    def __init__(self, store: HistoryStore | list[HistoryStore] | None):
        if store is None:
            self.stores: List[HistoryStore] = []
        elif isinstance(store, list):
            self.stores = store
        else:
            self.stores = [store]

    def load(self, session_id: str) -> List[ModelMessage]:
        for store in self.stores:
            messages = store.get(session_id)
            if messages:
                return messages
        return []

    async def save_from_result(
        self, session_id: str, all_messages: List[ModelMessage], MAX_HISTORY: int = 15
    ) -> List[ModelMessage]:
        cleaned = strip_tool_traffic(all_messages)
        cropped = await keep_recent_messages(cleaned, MAX_HISTORY=MAX_HISTORY)
        for store in self.stores:
            store.set(session_id, cropped)
        return cropped

    def reset(self, session_id: str) -> None:
        for store in self.stores:
            store.clear(session_id)
