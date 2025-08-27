import pytest
from typing import cast
from unittest.mock import MagicMock, AsyncMock

import httpx
import redis

from pydantic_ai.models.test import TestModel
from pydantic_ai.models import Model

from core.deps import Deps
from core.graph import (
    create_graph,
    run_with_memory,
    node_agent,
    node_tool,
    user_msg,
    assistant_msg,
    GraphState,
)


# ---------------------- fixtures ----------------------
@pytest.fixture
def deps() -> Deps:
    return Deps(
        http=MagicMock(spec=httpx.AsyncClient),
        redis=MagicMock(spec=redis.Redis),
        openai_api_key="dummy",
        telegram_bot_token="dummy",
    )


# ---------------------- tests de nodos ----------------------
@pytest.mark.asyncio
async def test_node_agent_basic(deps: Deps, monkeypatch):
    # Estado mínimo para el nodo agente
    state = GraphState(
        session_id="s1",
        user_input="hola",
        agent_output=None,
        tool_output=None,
        history=[user_msg("previo"), assistant_msg("previo_2")]
    )

    # Mock create_agent and its run method
    mock_agent_instance = MagicMock()
    mock_agent_instance.run.return_value = MagicMock(message="mocked agent output")
    monkeypatch.setattr("core.agents.create_agent", lambda: mock_agent_instance)

    # Forzamos que use TestModel via override dentro del nodo (el nodo ya crea TestModel)
    new_state = await node_agent(state, deps=deps)

    assert getattr(new_state, "agent_output", None)
    assert isinstance(new_state.agent_output, str)
    assert new_state.agent_output.strip() != ""
    assert new_state.agent_output == '{"dummy_tool":"TOOL_OK: Has llamado a una tool. Payload: "}'
    # Debe haber añadido mensajes al historial
    assert len(new_state.history) >= 2


@pytest.mark.asyncio
async def test_node_tool_basic(deps: Deps):
    # Simula que el agente ya generó una salida
    state = GraphState(
        session_id="s2",
        user_input="ping",
        agent_output="respuesta del agente",
        tool_output=None,
        history=[]
    )

    # El nodo tool invoca la dummy_tool con RunContext(TestModel())
    new_state = await node_tool(state, deps=deps)
    assert getattr(new_state, "tool_output", None)
    assert "TOOL_OK: Has llamado a una tool." in new_state.tool_output
    assert "respuesta del agente" in new_state.tool_output
    assert len(new_state.history) >= 1


# ---------------------- tests del grafo completo ----------------------
@pytest.mark.asyncio
async def test_create_graph_compiles(deps: Deps):
    graph, _deps = create_graph()
    # _deps es un Deps válido
    assert isinstance(_deps, Deps)
    # El grafo compilado debe tener ainvoke
    assert hasattr(graph, "ainvoke")


@pytest.mark.asyncio
async def test_run_with_memory_end_to_end(deps: Deps):
    graph, _deps = create_graph()

    # Memory manager doble: load sync, save async
    mm = MagicMock()
    mm.load.return_value = []
    mm.save_from_result = AsyncMock(return_value=None)

    out, history = await run_with_memory(
        graph_app=graph,
        deps=_deps,              # usamos los deps que devuelve create_graph
        mm=mm,
        session_id="sess-1",
        user_text="hola plantilla",
    )

    assert isinstance(out, str)
    assert out.strip() != ""
    assert isinstance(history, list)
    assert len(history) >= 2  # al menos user + assistant

    mm.load.assert_called_once_with("sess-1")
    mm.save_from_result.assert_awaited()


# ---------------------- test: forzar TestModel en agente del grafo ----------------------
@pytest.mark.asyncio
async def test_graph_with_testmodel_override(deps: Deps, monkeypatch):
    """
    Verifica que si forzamos TestModel para el agente dentro del nodo,
    todo sigue funcionando. Se mockea el create_agent para devolver
    un agente con override permanente a TestModel.
    """
    from core import agents as agents_mod

    real_create_agent = agents_mod.create_agent

    def fake_create_agent():
        ag = real_create_agent()
        # Dejamos un contexto override activo in-situ (sync) para run_sync
        # y en el nodo usamos run async: emplearemos monkeypatch para el run.
        return ag

    monkeypatch.setattr(agents_mod, "create_agent", fake_create_agent)

    graph, _deps = create_graph()
    mm = MagicMock()
    mm.load.return_value = []
    mm.save_from_result = AsyncMock(return_value=None)

    # Parcheamos el run del agente para garantizar TestModel
    from core.agents import create_agent as ca
    agent = ca()
    async def patched_run(*args, **kwargs):
        return await agent.run(*args, model=cast(Model, TestModel()), **kwargs)
    monkeypatch.setattr(agent, "run", patched_run, raising=False)

    # Ejecutamos pipeline
    out, history = await run_with_memory(
        graph_app=graph,
        deps=_deps,
        mm=mm,
        session_id="sess-2",
        user_text="hola",
    )

    assert isinstance(out, str)
    assert out.strip() != ""
    assert len(history) >= 2
