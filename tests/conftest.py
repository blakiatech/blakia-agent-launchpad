import pytest
from unittest.mock import AsyncMock
import httpx
import fakeredis
from core.deps import Deps

@pytest.fixture
def deps():
    return Deps(
        http=AsyncMock(spec=httpx.AsyncClient),
        redis=fakeredis.FakeRedis(decode_responses=True),
        openai_api_key="dummy",
        telegram_bot_token="dummy",
    )

@pytest.fixture
def redis_client():
    # para tests de redis_*
    return fakeredis.FakeRedis(decode_responses=True)