# cordobai/tests/test_redis_store.py
import fakeredis
import pytest
from typing_extensions import Protocol
from typing import cast
from core.memory.redis_history import RedisHistory
from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart, UserPromptPart
# ...


@pytest.fixture
def redis_client():
    return fakeredis.FakeRedis(decode_responses=True)


class Dumpable(Protocol):
    def model_dump_json(self) -> str: ...


def test_redis_history_cycle(redis_client):
    sid = "session_1"
    history = RedisHistory(sid, redis_client)
    messages = [
        ModelRequest(parts=[UserPromptPart("Hello")]),
        ModelResponse(parts=[TextPart("Hi there!")]),
    ]

    history._save(messages)
    loaded_messages = history._load()

    lm0 = cast(Dumpable, loaded_messages[0])
    lm1 = cast(Dumpable, loaded_messages[1])
    m0 = cast(Dumpable, messages[0])
    m1 = cast(Dumpable, messages[1])

    assert lm0.model_dump_json() == m0.model_dump_json()
    assert lm1.model_dump_json() == m1.model_dump_json()
