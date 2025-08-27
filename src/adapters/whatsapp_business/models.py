from pydantic import BaseModel, Field
from typing import List, Optional


class WhatsAppBase(BaseModel):
    object: str


class Change(BaseModel):
    value: dict
    field: str


class Entry(BaseModel):
    id: str
    changes: List[Change]


class Webhook(WhatsAppBase):
    entry: List[Entry]


class Message(BaseModel):
    from_number: str = Field(..., alias="from")
    id: str
    timestamp: str
    text: dict
    type: str


class Metadata(BaseModel):
    display_phone_number: str
    phone_number_id: str


class Value(BaseModel):
    messaging_product: str
    metadata: Metadata
    contacts: List[dict]
    messages: List[Message]


class OutgoingMessage(BaseModel):
    messaging_product: str = "whatsapp"
    to: str
    type: str
    text: Optional[dict] = None
