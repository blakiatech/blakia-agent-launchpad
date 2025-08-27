from core.memory.codec import (
    dumps_list,
    loads_list,
    dump_one_message_to_json,
    attach_model_dump_json_shim,
)
from pydantic_ai.messages import ModelRequest, UserPromptPart


def test_loads_list_handles_bytes_and_strings():
    msg = ModelRequest(parts=[UserPromptPart("hola")])
    json_items = dumps_list([msg])  # -> ["{...}"]
    # mezcla bytes y str
    raw_items = [json_items[0].encode("utf-8"), json_items[0]]
    msgs = loads_list(raw_items)
    assert len(msgs) == 2 and all(isinstance(m, ModelRequest) for m in msgs)


def test_dump_one_message_and_shim_addition():
    msg = ModelRequest(parts=[UserPromptPart("hola")])
    js = dump_one_message_to_json(msg)
    assert js.startswith("{") and "hola" in js

    attach_model_dump_json_shim()  # idempotente
    assert hasattr(msg, "model_dump_json")
    assert "hola" in msg.model_dump_json()
