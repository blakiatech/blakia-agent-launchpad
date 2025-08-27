# tests/test_in_memory_edges.py
from core.memory.in_memory import InMemoryHistory
from pydantic_ai.messages import ModelRequest, UserPromptPart


def test_in_memory_get_empty_and_clear_unknown():
    store = InMemoryHistory()
    assert store.get("nope") == []
    store.clear("nope")  # no revienta


def test_in_memory_add_single_message():
    store = InMemoryHistory()
    store.add("s", ModelRequest(parts=[UserPromptPart("hola")]))
    assert store.get("s")


def test_in_memory_set_falsy_to_empty_list():
    store = InMemoryHistory()
    store.set("s", None)
    assert store.get("s") == []
