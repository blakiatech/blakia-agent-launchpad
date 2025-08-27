import pytest
from pydantic_ai.tools import RunContext
from pydantic_ai.models.test import TestModel
from pydantic_ai.usage import RunUsage
from core.tools.dummy import dummy_tool
from core.deps import Deps
from unittest.mock import AsyncMock, MagicMock
import httpx
import redis

@pytest.fixture
def deps():
    return Deps(
        http=AsyncMock(spec=httpx.AsyncClient),
        redis=MagicMock(spec=redis.Redis),
        openai_api_key="dummy",
        telegram_bot_token="dummy",
    )

@pytest.fixture
def run_context(deps):
    return RunContext(deps=deps, model=TestModel(), usage=RunUsage())

@pytest.mark.asyncio
async def test_dummy_tool(run_context):
    out = await dummy_tool(run_context, payload="hola")
    assert "Has llamado a una tool" in out
    assert "hola" in out