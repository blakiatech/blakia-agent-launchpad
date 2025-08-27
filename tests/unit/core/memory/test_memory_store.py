import pytest
from unittest.mock import AsyncMock
from pydantic_ai.messages import ModelRequest, ModelResponse, UserPromptPart, TextPart

from core.memory.in_memory import InMemoryHistory
from core.memory.manager import MemoryManager


@pytest.fixture
def in_memory_store():
    return InMemoryHistory()


@pytest.fixture
def memory_manager(in_memory_store):
    return MemoryManager(store=in_memory_store)


def test_in_memory_history_cycle(in_memory_store):
    sid = "session_1"
    messages = [
        ModelRequest(parts=[UserPromptPart("Hello")]),
        ModelResponse(parts=[TextPart("Hi there!")]),
    ]

    in_memory_store.add(sid, messages)
    assert in_memory_store.get(sid) == messages

    new_messages = [ModelRequest(parts=[UserPromptPart("How are you?")])]
    in_memory_store.set(sid, new_messages)
    assert in_memory_store.get(sid) == new_messages

    in_memory_store.clear(sid)
    assert in_memory_store.get(sid) == []


def test_in_memory_history_multiple_sessions(in_memory_store):
    sid1 = "session_1"
    messages1 = [ModelRequest(parts=[UserPromptPart("Hello from session 1")])]
    in_memory_store.add(sid1, messages1)

    sid2 = "session_2"
    messages2 = [ModelRequest(parts=[UserPromptPart("Hello from session 2")])]
    in_memory_store.add(sid2, messages2)

    assert in_memory_store.get(sid1) == messages1
    assert in_memory_store.get(sid2) == messages2


@pytest.mark.asyncio
async def test_memory_manager_load_and_save(memory_manager, in_memory_store):
    sid = "session_1"
    messages = [
        ModelRequest(parts=[UserPromptPart("Hello")]),
        ModelResponse(parts=[TextPart("Hi there!")]),
    ]

    # Mock the async functions called by save_from_result
    memory_manager.keep_recent_messages = AsyncMock(return_value=messages)

    await memory_manager.save_from_result(sid, messages, MAX_HISTORY=15)
    loaded_messages = memory_manager.load(sid)

    assert loaded_messages == messages


def test_memory_manager_reset(memory_manager, in_memory_store):
    sid = "session_1"
    messages = [ModelRequest(parts=[UserPromptPart("Hello")])]
    in_memory_store.add(sid, messages)

    memory_manager.reset(sid)
    assert in_memory_store.get(sid) == []
