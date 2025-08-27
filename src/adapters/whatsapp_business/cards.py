# adapters/whatsapp_business/cards.py
from __future__ import annotations
from adapters.whatsapp_business.catalog import (
    OutgoingMessage,
    ButtonsMessage,
    ReplyButton,
    MediaHeader,
)


def dummy_card_message(to: str) -> OutgoingMessage:
    """
    Crea una tarjeta dummy de ejemplo, útil para pruebas rápidas.
    """
    body_text = (
        "👋 Hola!\n"
        "Soy una *tarjeta de prueba*.\n\n"
        "Este es un mensaje dummy para validar el envío de cards."
    )

    header = MediaHeader(
        kind="image",
        link="https://placekitten.com/400/300",  # Imagen de gatito dummy
    )

    buttons = [
        ReplyButton(id="dummy_ok", title="👍 Funciona"),
        ReplyButton(id="dummy_more", title="ℹ️ Más info"),
    ]

    footer_text = "Mensaje generado desde el dummy card"

    return OutgoingMessage(
        to=to,
        component=ButtonsMessage(
            body_text=body_text,
            header=header,
            buttons=buttons,
            footer_text=footer_text,
        ),
    )
