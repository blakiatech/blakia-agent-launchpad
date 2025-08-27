import pytest
from unittest.mock import AsyncMock
from core.memory.manager import MemoryManager, HistoryStore
from pydantic_ai.messages import ModelRequest, UserPromptPart


class DummyStore(HistoryStore):
    def __init__(self, data=None):
        self._d = data or {}

    def get(self, sid):
        return self._d.get(sid, [])

    def set(self, sid, msgs):
        self._d[sid] = list(msgs)

    def clear(self, sid):
        self._d.pop(sid, None)


@pytest.mark.asyncio
async def test_manager_load_prefers_first_non_empty_and_save_empty_is_ok(monkeypatch):
    s1 = DummyStore()
    s2 = DummyStore({"sid": [ModelRequest(parts=[UserPromptPart("x")])]})
    mm = MemoryManager([s1, s2])

    got = mm.load("sid")
    assert isinstance(got[0], ModelRequest)
    assert len(got[0].parts) == 1

    # keep_recent_messages -> []
    from core import agents as core_agents

    monkeypatch.setattr(core_agents, "keep_recent_messages", AsyncMock(return_value=[]))
    saved = await mm.save_from_result("sid", [])
    assert saved == []
    mm.reset("sid")  # no debe fallar
