# handler.py
import binascii
import logging
import hmac
import hashlib
from typing import Any, Dict, Optional

from fastapi import APIRouter, Request, Response, HTTPException, Depends

# --- Tu stack ---
from core.memory import get_memory_store
from core.memory.manager import MemoryManager, HistoryStore
from core.graph import run_with_memory, create_graph
from infrastructure.settings import settings

from adapters.whatsapp_business.catalog import OutgoingMessage, TextMessage
from .client import send_catalog_message

router = APIRouter()

# Crear una instancia de la aplicación y los dependencias
graph, deps = create_graph()


# ======================================================
# Helpers
# ======================================================
def get_memory_manager() -> MemoryManager:
    base_store = get_memory_store()
    stores: list[HistoryStore] = []
    if isinstance(base_store, list):
        stores.extend(base_store)
    elif base_store is not None:
        stores.append(base_store)
    return MemoryManager(store=stores)


def _calc_sig(app_secret: str, raw: bytes) -> str:
    return hmac.new(app_secret.encode(), raw, hashlib.sha256).hexdigest()


def verify_whatsapp_signature(
    app_secret: str, raw_body: bytes, signature_header: str
) -> tuple[bool, str, str]:
    try:
        provided_sig = (signature_header or "").split("=", 1)[1]
    except Exception:
        return False, "", ""
    expected = _calc_sig(app_secret, raw_body)
    return hmac.compare_digest(expected, provided_sig), provided_sig, expected


async def verify_signature(request: Request):
    raw = await request.body()
    sig_hdr = request.headers.get("X-Hub-Signature-256", "")

    if not settings.meta_app_secret:
        logging.error("META_APP_SECRET no configurado")
        raise HTTPException(
            status_code=400, detail="Server misconfigured (no app secret)"
        )

    ok, provided, expected = verify_whatsapp_signature(
        settings.meta_app_secret, raw, sig_hdr
    )
    if not ok:
        logging.error(
            "Firma inválida: provided=%s expected=%s raw_len=%d first16=%s hdr=%r",
            (provided[:12] + "...") if provided else "<none>",
            (expected[:12] + "...") if expected else "<none>",
            len(raw),
            binascii.hexlify(raw[:16]).decode(),
            sig_hdr,
        )
        raise HTTPException(status_code=400, detail="Invalid signature")


def pick_value(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        return body["entry"][0]["changes"][0]["value"]
    except Exception:
        return None


def pick_first_message(value: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    msgs = value.get("messages") or []
    return msgs[0] if msgs else None


def pick_contact(value: Dict[str, Any]) -> Dict[str, Any]:
    contacts = value.get("contacts") or [{}]
    return contacts[0]


def extract_user_text(msg: Dict[str, Any]) -> str:
    t = msg.get("type")
    if t == "text":
        return msg["text"]["body"]

    if t == "interactive":
        inter = msg.get("interactive") or {}
        if "button_reply" in inter:
            r = inter["button_reply"]
            return f"[button:{r.get('id')}] {r.get('title')}"
        if "list_reply" in inter:
            r = inter["list_reply"]
            return f"[list:{r.get('id')}] {r.get('title')}"
        return "[interactive]"

    if t == "image":
        cap = (msg.get("image") or {}).get("caption")
        return cap or "[image]"

    if t == "reaction":
        return f"[reaction] {msg.get('reaction', {}).get('emoji')}"

    if t == "location":
        loc = msg.get("location") or {}
        return f"[location] {loc.get('latitude')},{loc.get('longitude')}"

    return f"[{t}]"


# ======================================================
# Webhook
# ======================================================
@router.post("/webhook", dependencies=[Depends(verify_signature)])
async def webhook_post(
    request: Request, mm: MemoryManager = Depends(get_memory_manager)
):
    try:
        body = await request.json()
    except Exception:
        logging.warning("POST /webhook: cuerpo no JSON o vacío")
        return Response(status_code=200)

    value = pick_value(body)
    if not value:
        logging.warning("POST /webhook: sin 'value' utilizable en payload")
        return Response(status_code=200)

    msg = pick_first_message(value)
    if not msg:
        logging.info("POST /webhook: 'messages' vacío")
        return Response(status_code=200)

    contact = pick_contact(value)
    wa_id = contact.get("wa_id")
    
    # Ensure wa_id is not None
    if not wa_id:
        logging.warning("POST /webhook: missing wa_id in contact")
        return Response(status_code=200)

    user_text = extract_user_text(msg)
    logging.info("IN: wa_id=%s kind=%s text=%r", wa_id, msg.get("type"), user_text)

    # Ejecuta tu pipeline
    try:
        reply_text, _ctx = await run_with_memory(
            graph,
            deps,
            mm,
            session_id=wa_id,
            user_text=user_text,
        )
    except Exception as e:
        logging.exception("run_graph_with_memory failed: %s", e)
        reply_text = "Ha ocurrido un error momentáneo. Intenta de nuevo."

    # Construir mensaje con el catálogo
    out_msg = OutgoingMessage(to=wa_id, component=TextMessage(body=reply_text))

    try:
        out = await send_catalog_message(out_msg)
        logging.info("OUT ok: %s", out)
    except Exception as e:
        logging.exception("send_message failed: %s", e)

    return Response(status_code=200)


@router.get("/webhook")
def webhook_get(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        logging.info("WEBHOOK_VERIFIED")
        return Response(content=challenge, status_code=200)

    logging.info(
        "VERIFICATION_FAILED: mode=%r token_ok=%s",
        mode,
        token == settings.whatsapp_verify_token,
    )
    raise HTTPException(status_code=403, detail="Verification failed")

