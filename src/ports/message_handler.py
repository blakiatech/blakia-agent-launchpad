# src/ports/message_handler.py
from __future__ import annotations
from typing import Protocol, Any

class MessageHandler(Protocol):
    async def handle_message(self, session_id: str, user_text: str) -> tuple[str, Any]: ...
