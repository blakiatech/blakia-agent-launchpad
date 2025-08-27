from __future__ import annotations
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

router = APIRouter()

GENERIC_HEADER = "x-api-key"

class WebhookIn(BaseModel):
    session_id: str
    message: str

class WebhookOut(BaseModel):
    response: str

def _check_api_key(x_api_key: str | None) -> None:
    # En el template dummy, basta con comprobar que existe el header
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing x-api-key")

@router.post("/generic-webhook", response_model=WebhookOut)
async def generic_webhook(payload: WebhookIn, x_api_key: str | None = Header(None, alias=GENERIC_HEADER)):
    _check_api_key(x_api_key)
    # Respuesta mínima para smoke tests
    return WebhookOut(response=f"Agente dummy recibió: {payload.message}")
