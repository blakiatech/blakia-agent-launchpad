from ports.outbound import CatalogSender
from adapters.whatsapp_business.client import send_catalog_message as _send
from adapters.whatsapp_business.catalog import OutgoingMessage


class WhatsAppCatalogSender(CatalogSender):
    async def send_catalog_message(self, payload: OutgoingMessage) -> None:
        await _send(payload)