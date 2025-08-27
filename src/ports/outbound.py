from adapters.whatsapp_business.catalog import OutgoingMessage


class CatalogSender:
    async def send_catalog_message(self, payload: OutgoingMessage) -> None: ...