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

@pytest.fixture(autouse=True)
def _block_network_in_unit(request, monkeypatch):
    if "unit" in request.keywords:
        try:
            import httpx
            def _blocked(*a, **k):
                raise RuntimeError("Network blocked in unit tests")
            for name in ("get","post","put","delete","patch","stream"):
                if hasattr(httpx, name):
                    monkeypatch.setattr(httpx, name, _blocked, raising=True)
        except Exception:
            pass
