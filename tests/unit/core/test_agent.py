import pytest
from typing import cast
from unittest.mock import MagicMock

import httpx
import redis

from pydantic_ai.models.test import TestModel
from pydantic_ai import RunContext
from pydantic_ai.models import Model
from pydantic_ai.usage import RunUsage

from core.deps import Deps
from core.agents import create_agent
from core.tools.dummy import dummy_tool


@pytest.fixture
def mock_deps() -> Deps:
    # Para el dummy setup no necesitamos clientes reales
    mock_http_client = MagicMock(spec=httpx.AsyncClient)
    mock_redis_client = MagicMock(spec=redis.Redis)
    return Deps(
        http=mock_http_client,
        redis=mock_redis_client,
        openai_api_key="dummy",
        telegram_bot_token="dummy",
        empresas_api_token=None,
        catalog_sender=None,
        model=None,  # opcional
    )


@pytest.fixture
def dummy_agent():
    # Construimos el agente de la plantilla
    return create_agent()


def test_agent_sync_basic(dummy_agent):
    """
    Con TestModel, el agente debe devolver siempre un string no vacío.
    """
    tm = TestModel()
    res = dummy_agent.run_sync("hola plantilla", model=tm)
    assert isinstance(res.output, str)
    assert res.output.strip() != ""


@pytest.mark.asyncio
async def test_agent_async_basic(dummy_agent):
    """
    Versión async del test básico.
    """
    tm = TestModel()
    res = await dummy_agent.run("ping", model=tm)
    assert isinstance(res.output, str)
    assert res.output.strip() != ""


def test_agent_override_context(dummy_agent):
    """
    override(model=TestModel()) debe funcionar en contexto sync.
    """
    tm = TestModel()
    with dummy_agent.override(model=tm):
        res = dummy_agent.run_sync("hola override")
        assert isinstance(res.output, str)
        assert res.output.strip() != ""


@pytest.mark.asyncio
async def test_dummy_tool_direct(mock_deps):
    """
    Llamamos a la tool dummy directamente con RunContext.
    Debe devolver el texto prefijado con el payload.
    """
    run_ctx = RunContext(
        deps=mock_deps,
        model=cast(Model, TestModel()),
        usage=RunUsage(),
    )
    payload = "payload de prueba"
    out = await dummy_tool(run_ctx, payload=payload)
    assert isinstance(out, str)
    assert "TOOL_OK: Has llamado a una tool." in out  # coincide con el texto de la tool
    assert payload in out
