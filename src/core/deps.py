# src/core/deps.py
from __future__ import annotations
from pydantic.dataclasses import dataclass
from typing import Optional, Any

import httpx
from ports.outbound import CatalogSender

@dataclass(config=dict(arbitrary_types_allowed=True))
class Deps:
    http: Optional[httpx.AsyncClient] = None
    redis: Optional[Any] = None
    openai_api_key: Optional[str] = None
    telegram_bot_token: Optional[str] = None

    # Para el template: en vez de un objeto Model, exponemos un nombre de modelo.
    # P. ej. "test" en CI, o "openai:gpt-4.1-mini" en real.
    model_name: Optional[str] = "test"

    # Campos opcionales que podrías querer inyectar más tarde
    empresas_api_token: Optional[str] = None
    catalog_sender: Optional[CatalogSender] = None

    # Cualquier otro state o config libre
    extra: Any = None
