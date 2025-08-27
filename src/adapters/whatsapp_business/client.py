from __future__ import annotations
import asyncio
import logging
import re
from typing import Any, Dict

import httpx
from infrastructure.settings import settings
from adapters.whatsapp_business.catalog import OutgoingMessage  # ✅ tu catálogo

# =====================================================
# Utils
# =====================================================


def _endpoint() -> str:
    return (
        f"https://graph.facebook.com/"
        f"{settings.whatsapp_api_version}/"
        f"{settings.whatsapp_phone_id}/messages"
    )


def _headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json",
    }


def _normalize_to(to: str) -> str:
    """Formato E.164 sin '+' (ej. +34699111222 -> 34699111222)."""
    return re.sub(r"^\+", "", (to or "").strip())


def _should_retry(status: int) -> bool:
    return status in (429, 500, 502, 503, 504)


def _shorten(s: str, limit: int = 120) -> str:
    if not s:
        return ""
    s = str(s)
    return s if len(s) <= limit else s[:limit] + "…"


# =====================================================
# Payload Builders (mínimos de conveniencia)
# =====================================================
def get_text_message_input(
    to: str, body: str, preview_url: bool = False
) -> Dict[str, Any]:
    safe_body = (body or "").strip() or " "
    if len(safe_body) > 4000:
        safe_body = safe_body[:4000] + "…"
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": _normalize_to(to),
        "type": "text",
        "text": {"preview_url": preview_url, "body": safe_body},
    }


# =====================================================
# Core Sender
# =====================================================
async def send_message(
    payload: Dict[str, Any],
    *,
    timeout: float = 30.0,
    retries: int = 2,
    backoff: float = 1.5,
) -> Dict[str, Any]:
    """
    Envía un payload ya construido (dict).
    Devuelve la respuesta JSON (o lanza excepción con logging).
    """
    url, headers = _endpoint(), _headers()

    # Debug de request
    try:
        to_dbg = payload.get("to") or "<no-to>"
        msg_type = payload.get("type")
        body_dbg = ""
        if msg_type == "text":
            body_dbg = _shorten(payload.get("text", {}).get("body", ""))
        logging.info(
            "WA SEND -> %s to=%s type=%s body=%r", url, to_dbg, msg_type, body_dbg
        )
    except Exception:
        logging.info("WA SEND -> %s payload_keys=%s", url, list(payload.keys()))

    attempt = 0
    last_exc: Exception | None = None
    async with httpx.AsyncClient(timeout=timeout) as client:
        while attempt <= retries:
            attempt += 1
            try:
                resp = await client.post(url, headers=headers, json=payload)
                try:
                    data = resp.json()
                except Exception:
                    data = {"raw": resp.text}

                if resp.status_code >= 400:
                    logging.error("WA RESP <- %s %s", resp.status_code, data)
                    if attempt <= retries and _should_retry(resp.status_code):
                        await asyncio.sleep(backoff ** (attempt - 1))
                        continue
                    resp.raise_for_status()
                else:
                    logging.info("WA RESP <- %s %s", resp.status_code, data)
                    return data

            except (httpx.TimeoutException, httpx.ReadTimeout) as e:
                logging.error("WA TIMEOUT (%d/%d): %s", attempt, retries, e)
                last_exc = e
                if attempt <= retries:
                    await asyncio.sleep(backoff ** (attempt - 1))
                    continue
                raise
            except httpx.RequestError as e:
                logging.error("WA REQUEST ERROR (%d/%d): %s", attempt, retries, e)
                last_exc = e
                if attempt <= retries:
                    await asyncio.sleep(backoff ** (attempt - 1))
                    continue
                raise

    if last_exc:
        raise last_exc
    raise RuntimeError("send_message: unknown error")


# =====================================================
# Catálogo integration
# =====================================================
async def send_catalog_message(msg: OutgoingMessage, **kwargs) -> Dict[str, Any]:
    """
    Envía un mensaje definido con el catálogo (OutgoingMessage + component).
    """
    payload = msg.build()
    return await send_message(payload, **kwargs)
