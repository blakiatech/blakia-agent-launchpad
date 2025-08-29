"""
This module is the implementation of the outbound port for sending messages via WhatsApp.
It acts as a translator from core-defined, generic data structures (like Card)
to WhatsApp-specific message objects.
"""
from typing import Iterable
from ports.messages import MessageSender, Card
from adapters.whatsapp_business.client import send_catalog_message as _send
from adapters.whatsapp_business.catalog import (
    OutgoingMessage,
    TextMessage,
    ButtonsMessage,
    ReplyButton,
    MediaHeader,
)


class WhatsAppMessageSender(MessageSender):
    """
    The adapter that implements the MessageSender port for the WhatsApp Business API.
    """

    async def send_text(self, chat_id: str, text: str) -> None:
        """
        Translates a generic text message into a WhatsApp-specific TextMessage
        and sends it.
        """
        # 1. Translate from generic string to WhatsApp-specific component
        component = TextMessage(body=text)

        # 2. Wrap in an OutgoingMessage envelope
        whatsapp_message = OutgoingMessage(to=chat_id, component=component)

        # 3. Send using the client
        await _send(whatsapp_message)

    async def send_cards(self, chat_id: str, cards: Iterable[Card]) -> None:
        """
        Translates a generic Card object into a WhatsApp-specific ButtonsMessage
        and sends it for each card.
        """
        for card in cards:
            # 1. Translate generic Card actions to WhatsApp ReplyButtons
            buttons = [
                ReplyButton(id=action.get("value", ""), title=action.get("label", ""))
                for action in card.get("actions", [])
                if action.get("type") == "reply"
            ]

            # 2. Create the ButtonsMessage component
            component = ButtonsMessage(
                body_text=card.get("description") or card.get("title", ""),
                buttons=buttons,
            )

            # 3. Add an image header if present in the generic Card
            if card.get("image_url"):
                component.header = MediaHeader(
                    kind="image", link=card["image_url"]
                )
            
            # 4. Wrap in an OutgoingMessage envelope
            whatsapp_message = OutgoingMessage(to=chat_id, component=component)

            # 5. Send using the client
            await _send(whatsapp_message)

