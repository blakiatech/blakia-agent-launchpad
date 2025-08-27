# src/ports/messages.py
from __future__ import annotations
from typing import Protocol, TypedDict, Iterable, Optional


class Action(TypedDict, total=False):
    type: str           # "url" | "reply" | "call" | ...
    label: str
    value: Optional[str]


class Card(TypedDict, total=False):
    title: str
    description: Optional[str]
    url: Optional[str]
    image_url: Optional[str]
    actions: list[Action]


class MessageSender(Protocol):
    async def send_text(self, chat_id: str, text: str) -> None: ...
    async def send_cards(self, chat_id: str, cards: Iterable[Card]) -> None: ...

