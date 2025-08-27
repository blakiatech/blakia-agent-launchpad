# whatsappMessages/catalog.py
from __future__ import annotations
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, HttpUrl, field_validator


# =========================
# Base
# =========================
class MessageComponent(BaseModel):
    def to_payload(self) -> Dict[str, Any]:
        raise NotImplementedError


# =========================
# Text
# =========================
class TextMessage(MessageComponent):
    body: str
    preview_url: bool = False

    def to_payload(self) -> Dict[str, Any]:
        return {
            "type": "text",
            "text": {"body": self.body, "preview_url": self.preview_url},
        }


# =========================
# Image
# =========================
class ImageMessage(MessageComponent):
    link: HttpUrl
    caption: Optional[str] = None

    def to_payload(self) -> Dict[str, Any]:
        p: Dict[str, Any] = {"type": "image", "image": {"link": str(self.link)}}
        if self.caption:
            p["image"]["caption"] = self.caption
        return p


# =========================
# Document
# =========================
class DocumentMessage(MessageComponent):
    link: HttpUrl
    filename: Optional[str] = None
    caption: Optional[str] = None

    def to_payload(self) -> Dict[str, Any]:
        doc: Dict[str, Any] = {"link": str(self.link)}
        if self.filename:
            doc["filename"] = self.filename
        if self.caption:
            doc["caption"] = self.caption
        return {"type": "document", "document": doc}


# =========================
# Buttons
# =========================
class ReplyButton(BaseModel):
    id: str
    title: str

    @field_validator("title")
    @classmethod
    def _title_len(cls, v: str) -> str:
        if len(v) > 20:
            raise ValueError("El título del botón debe tener ≤ 20 caracteres.")
        return v


class MediaHeader(BaseModel):
    kind: Literal["text", "image", "video", "document"]
    text: Optional[str] = None
    link: Optional[HttpUrl] = None

    @field_validator("text")
    @classmethod
    def _text_required_for_text_kind(cls, v, info):
        if info.data.get("kind") == "text" and not v:
            raise ValueError("Header 'text' requiere 'text'.")
        return v

    @field_validator("link")
    @classmethod
    def _link_required_for_media_kind(cls, v, info):
        if info.data.get("kind") in ("image", "video", "document") and not v:
            raise ValueError("Header media requiere 'link'.")
        return v


class ButtonsMessage(MessageComponent):
    body_text: str
    footer_text: Optional[str] = None
    buttons: List[ReplyButton]
    header: Optional[MediaHeader] = None

    def to_payload(self) -> Dict[str, Any]:
        buttons_payload = [
            {"type": "reply", "reply": b.model_dump()} for b in self.buttons
        ]
        interactive: Dict[str, Any] = {
            "type": "button",
            "body": {"text": self.body_text},
            "action": {"buttons": buttons_payload},
        }
        if self.footer_text:
            interactive["footer"] = {"text": self.footer_text}
        if self.header:
            if self.header.kind == "text":
                interactive["header"] = {"type": "text", "text": self.header.text}
            elif self.header.kind == "image":
                interactive["header"] = {
                    "type": "image",
                    "image": {"link": str(self.header.link)},
                }
            elif self.header.kind == "video":
                interactive["header"] = {
                    "type": "video",
                    "video": {"link": str(self.header.link)},
                }
            elif self.header.kind == "document":
                interactive["header"] = {
                    "type": "document",
                    "document": {"link": str(self.header.link)},
                }
        return {"type": "interactive", "interactive": interactive}


# =========================
# Video
# =========================
class VideoMessage(MessageComponent):
    link: HttpUrl
    caption: Optional[str] = None  # opcional; no confundir con header de interactivos

    def to_payload(self) -> Dict[str, Any]:
        p: Dict[str, Any] = {"type": "video", "video": {"link": str(self.link)}}
        if self.caption:
            p["video"]["caption"] = self.caption
        return p


# =========================
# Audio
# =========================
class AudioMessage(MessageComponent):
    link: HttpUrl  # MP3/OGG/OPUS soportados por WA Cloud

    def to_payload(self) -> Dict[str, Any]:
        return {"type": "audio", "audio": {"link": str(self.link)}}


# =========================
# Sticker (WEBP)
# =========================
class StickerMessage(MessageComponent):
    link: HttpUrl  # webp público

    def to_payload(self) -> Dict[str, Any]:
        return {"type": "sticker", "sticker": {"link": str(self.link)}}


# =========================
# Location
# =========================
class LocationMessage(MessageComponent):
    latitude: float
    longitude: float
    name: Optional[str] = None
    address: Optional[str] = None

    def to_payload(self) -> Dict[str, Any]:
        loc: Dict[str, Any] = {"latitude": self.latitude, "longitude": self.longitude}
        if self.name:
            loc["name"] = self.name
        if self.address:
            loc["address"] = self.address
        return {"type": "location", "location": loc}


# =========================
# Contacts (vCard simple)
# =========================
class ContactPhone(BaseModel):
    phone: str
    type: Optional[Literal["CELL", "WORK", "HOME"]] = None
    wa_id: Optional[str] = None  # si ya es usuario de WA, opcional


class ContactName(BaseModel):
    formatted_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class Contact(BaseModel):
    name: ContactName
    phones: List[ContactPhone]


class ContactsMessage(MessageComponent):
    contacts: List[Contact]

    def to_payload(self) -> Dict[str, Any]:
        return {
            "type": "contacts",
            "contacts": [c.model_dump(exclude_none=True) for c in self.contacts],
        }


# =========================
# Reaction (emoji a un mensaje existente)
# =========================
class ReactionMessage(MessageComponent):
    message_id: str  # wamid del mensaje al que reaccionas
    emoji: str  # p.ej. "👍", "❤️"

    def to_payload(self) -> Dict[str, Any]:
        return {
            "type": "reaction",
            "reaction": {"message_id": self.message_id, "emoji": self.emoji},
        }


# =========================
# List
# =========================
class ListSectionRow(BaseModel):
    id: str
    title: str
    description: Optional[str] = None


class ListSection(BaseModel):
    title: str
    rows: List[ListSectionRow]


class ListMessage(MessageComponent):
    body_text: str
    button_text: str
    sections: List[ListSection]
    header_text: Optional[str] = None
    footer_text: Optional[str] = None

    @field_validator("button_text")
    @classmethod
    def _btn_len(cls, v: str) -> str:
        if len(v) > 20:
            raise ValueError("El texto del botón de lista debe tener ≤ 20 caracteres.")
        return v

    def to_payload(self) -> Dict[str, Any]:
        interactive: Dict[str, Any] = {
            "type": "list",
            "body": {"text": self.body_text},
            "action": {
                "button": self.button_text,
                "sections": [
                    {
                        "title": s.title,
                        "rows": [r.model_dump(exclude_none=True) for r in s.rows],
                    }
                    for s in self.sections
                ],
            },
        }
        if self.header_text:
            interactive["header"] = {"type": "text", "text": self.header_text}
        if self.footer_text:
            interactive["footer"] = {"text": self.footer_text}
        return {"type": "interactive", "interactive": interactive}


# =========================
# Template (HSM)
# =========================
class TemplateMessage(MessageComponent):
    name: str
    language_code: str = "en_US"
    components: Optional[List[Dict[str, Any]]] = None

    def to_payload(self) -> Dict[str, Any]:
        t: Dict[str, Any] = {
            "type": "template",
            "template": {"name": self.name, "language": {"code": self.language_code}},
        }
        if self.components:
            t["template"]["components"] = self.components
        return t


# =========================
# Business Card
# =========================
class BusinessCardMessage(MessageComponent):
    name: str
    address: str
    phone: str
    url: str
    image: HttpUrl

    def to_payload(self) -> Dict[str, Any]:
        # This is a simplified representation.
        # WhatsApp doesn't have a dedicated "business card" message type.
        # We can use a text message with a formatted body and a header image.

        # Create a formatted text body
        body = f"*{self.name}*\n{self.address}\n{self.phone}\n{self.url}"

        # Use a ButtonsMessage with a header image and a link button
        interactive = {
            "type": "button",
            "header": {"type": "image", "image": {"link": str(self.image)}},
            "body": {"text": body},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {"id": "view_website", "title": "Visit Website"},
                    }
                ]
            },
        }
        return {"type": "interactive", "interactive": interactive}


class OutgoingMessage(BaseModel):
    to: str
    component: MessageComponent
    context_message_id: Optional[str] = None

    def build(self) -> Dict[str, Any]:
        root: Dict[str, Any] = {"messaging_product": "whatsapp", "to": self.to}
        root.update(self.component.to_payload())
        if self.context_message_id:
            root["context"] = {"message_id": self.context_message_id}
        return root
