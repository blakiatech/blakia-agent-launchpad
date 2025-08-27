# src/adapters/telegram/handler.py
"""Telegram webhook handler (APIRouter). Opción A mínima.

- Config vía os.environ (migrar a settings en Opción B).
- Grafo creado en import (migrar a carga perezosa en Opción B).
- Envío directo a la API de Telegram (migrar a sender.py + puerto MessageSender en Opción B).

Si no hay TELEGRAM_BOT_TOKEN:
- El router puede seguir montado (recibe webhooks), pero el envío será NO-OP (no envía).
- Recomendado además: en infrastructure.server montar el router solo si hay token.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
import os
import httpx
from typing import Optional
from core.memory import get_memory_store
from core.memory.manager import MemoryManager, HistoryStore
from core.graph import create_graph, run_with_memory

router = APIRouter()

# ⚠️ Opción A: carga del grafo en import (rápido, pero puede ser costoso).
# 👉 Opción B: usa un singleton perezoso get_graph_and_deps() para inicializar on-demand.
graph, deps = create_graph()

# ⚠️ Opción A: config vía env (simple).
# 👉 Opción B: mover a infrastructure/settings.py con env_prefix BLAKIA_*
TELEGRAM_BOT_TOKEN: Optional[str] = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_SECRET_TOKEN: Optional[str] = os.environ.get("TELEGRAM_SECRET_TOKEN")  # opcional pero recomendado

TELEGRAM_API_BASE: Optional[str]

if TELEGRAM_BOT_TOKEN:
    TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
else:
    TELEGRAM_API_BASE = None  # sin token → API deshabilitada (NO-OP al enviar)
    # También puedes evitar montar el router desde infrastructure.server.

class TGUpdate(BaseModel):
    """Subset del Update de Telegram que nos interesa en Opción A."""
    update_id: int | None = None
    message: dict | None = None
    edited_message: dict | None = None
    channel_post: dict | None = None
    # (amplía si necesitas: callback_query, inline_query, etc.)


async def verify_tg_secret(x_telegram_bot_api_secret_token: str | None = Header(None)):
    """Verifica el secret header del webhook de Telegram (si está configurado).

    Configúralo al registrar el webhook con Telegram:
    setWebhook?url=...&secret_token=TU_SECRETO

    Telegram enviará ese valor en el header `X-Telegram-Bot-Api-Secret-Token`.
    """
    if not TELEGRAM_SECRET_TOKEN:
        return  # auth deshabilitada si no configuraste secreto
    if x_telegram_bot_api_secret_token != TELEGRAM_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid Telegram secret token")


def get_memory_manager() -> MemoryManager:
    """Crear MemoryManager con el/los store(s) configurados."""
    base_store = get_memory_store()
    stores: list[HistoryStore] = []
    if isinstance(base_store, list):
        stores.extend(base_store)
    elif base_store is not None:
        stores.append(base_store)
    return MemoryManager(store=stores)


async def tg_send_text(chat_id: int | str, text: str) -> None:
    """Opción A: envío directo vía API de Telegram.

    👉 Opción B: mover a adapters/telegram/sender.py e implementar el puerto MessageSender.
    """
    if not TELEGRAM_API_BASE:
        # NO-OP si no hay token; el servidor sigue funcionando.
        # (Recomendado además: no montar este router si no hay token.)
        print("⚠️ Telegram disabled: no TELEGRAM_BOT_TOKEN configured; skipping send.")
        return

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            f"{TELEGRAM_API_BASE}/sendMessage",
            json={"chat_id": chat_id, "text": text},
        )
        r.raise_for_status()


def _extract_chat_and_text(update: TGUpdate) -> tuple[int | None, str | None]:
    """Extrae chat_id y texto desde las variantes de Update más comunes."""
    msg = update.message or update.edited_message or update.channel_post
    if not msg:
        return None, None
    chat = msg.get("chat") or {}
    chat_id = chat.get("id")
    text = msg.get("text")
    return chat_id, text


@router.post("/webhook")
async def telegram_webhook(
    payload: TGUpdate,
    _=Depends(verify_tg_secret),
    mm: MemoryManager = Depends(get_memory_manager),
):
    """Procesa un Update de Telegram y responde usando tu grafo."""
    chat_id, text = _extract_chat_and_text(payload)
    if not chat_id or not text:
        # Nada que procesar: confirmamos para que Telegram no reintente en bucle.
        return {"ok": True}

    # Comandos simples (ejemplo mínimo)
    if text.strip().lower() in {"/start", "start"}:
        await tg_send_text(chat_id, "¡Hola! Envía tu consulta.")
        return {"ok": True}

    # Usamos el chat_id como session_id para mantener memoria por conversación
    session_id = str(chat_id)

    reply, _history = await run_with_memory(graph, deps, mm, session_id, text)

    # En Opción A respondemos enviando un mensaje posterior vía API (NO-OP si no hay token).
    await tg_send_text(chat_id, reply)

    # Telegram espera 200 OK; devolver JSON es opcional
    return {"ok": True}

