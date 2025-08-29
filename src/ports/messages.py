# src/ports/messages.py
from __future__ import annotations
from typing import TypedDict, Iterable, Optional


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


class MessageSender:
    async def send_text(self, chat_id: str, text: str) -> None:
        raise NotImplementedError

    async def send_cards(self, chat_id: str, cards: Iterable[Card]) -> None:
        raise NotImplementedError

