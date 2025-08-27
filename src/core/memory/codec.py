# core/memory/codec.py
"""
Este módulo proporciona funciones para serializar y deserializar mensajes
utilizando JSON, facilitando la comunicación entre componentes.
"""

from __future__ import annotations
import json
from typing import List
from pydantic_ai.messages import (
    ModelMessage,
    ModelMessagesTypeAdapter,
    ModelRequest,
    ModelResponse,
)


# ---------- API de serialización común ----------


def dumps_list(messages: List[ModelMessage]) -> list[str]:
    """
    Convierte una lista de ModelMessage en una lista de strings JSON,
    uno por mensaje (formato objeto JSON).
    """
    if not messages:
        return []
    arr_bytes = ModelMessagesTypeAdapter.dump_json(messages)  # b'[ {...}, {...} ]'
    objs = json.loads(arr_bytes)
    return [json.dumps(o, ensure_ascii=False) for o in objs]


def loads_list(raw_items: list[str | bytes]) -> List[ModelMessage]:
    """
    Convierte una lista de strings/bytes JSON (uno por mensaje) en ModelMessage[].
    Tolerante a bytes y a algunos errores de parseo.
    """
    out: List[ModelMessage] = []
    for raw in raw_items:
        s = (
            raw.decode("utf-8", errors="replace")
            if isinstance(raw, (bytes, bytearray))
            else str(raw)
        )
        try:
            obj = json.loads(s)
            msg = ModelMessagesTypeAdapter.validate_python([obj])[0]
        except Exception:
            # fallback si viene raro pero casi-json
            msg = ModelMessagesTypeAdapter.validate_json(f"[{s}]")[0]
        out.append(msg)
    return out


def dump_one_message_to_json(msg: ModelMessage) -> str:
    """Serializa un único mensaje a JSON objeto (string) usando el adapter de lista."""
    return dumps_list([msg])[0]


# ---------- Shim opcional para tests/compatibilidad ----------


def attach_model_dump_json_shim() -> None:
    """
    Añade .model_dump_json() a ModelRequest/ModelResponse (y Tool* si existen)
    sin romper si ya existe. Permite comparaciones en tests.
    """

    def _attach(cls):
        if not hasattr(cls, "model_dump_json"):

            def _model_dump_json(self):
                return dump_one_message_to_json(self)

            setattr(cls, "model_dump_json", _model_dump_json)

    _TOOL_CLASSES = ()
    for _cls in (ModelRequest, ModelResponse) + _TOOL_CLASSES:
        _attach(_cls)


# Ejecutar shim al importar si quieres compatibilidad transparente
attach_model_dump_json_shim()
