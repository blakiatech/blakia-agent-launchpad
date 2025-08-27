# src/core/graph.py
from __future__ import annotations
from typing import Any, List, Tuple, Optional

from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    UserPromptPart,
    TextPart,
    ModelMessagesTypeAdapter,
)
from pydantic_ai import RunContext
from pydantic_ai.usage import RunUsage
from pydantic_ai.models.test import TestModel  # modelo concreto para tools

from core.agents import create_agent
from core.deps import Deps
from core.tools.dummy import dummy_tool


# -------- util mensajes --------
def user_msg(text: str) -> ModelRequest:
    return ModelRequest(parts=[UserPromptPart(text)])

def assistant_msg(text: str) -> ModelResponse:
    return ModelResponse(parts=[TextPart(text)])


# -------- estado del grafo --------
class GraphState(BaseModel):
    session_id: str
    user_input: str
    agent_output: Optional[str] = None
    tool_output: Optional[str] = None
    history: List[ModelMessage] = Field(default_factory=list)


# -------- nodos puros (reciben deps) --------
async def node_agent(state: GraphState, deps: Deps) -> GraphState:
    """
    Ejecuta el agente dummy. Para tipado correcto con pydantic-ai:
    pasamos el modelo por nombre en `agent.run(..., model=...)`.
    """
    agent = create_agent()  # el propio agente tiene su modelo por defecto
    run_model = deps.model_name or "test"
    result = await agent.run(state.user_input, model=run_model)
    reply_text = result.output or ""
    new_hist = (state.history or []) + [user_msg(state.user_input), assistant_msg(reply_text)]
    return state.model_copy(update={"agent_output": reply_text, "history": new_hist})


async def node_tool(state: GraphState, deps: Deps) -> GraphState:
    """
    Llama explícitamente a la tool dummy (plantilla).
    Para RunContext.model usamos TestModel(), que es concreto y tipa bien.
    """
    run_ctx = RunContext(
        deps=deps,
        model=TestModel(),           # evita abstractos; mypy OK
        usage=RunUsage(),
    )
    tool_reply = await dummy_tool(run_ctx, payload=state.agent_output or "")
    new_hist = (state.history or []) + [assistant_msg(tool_reply)]
    return state.model_copy(update={"tool_output": tool_reply, "history": new_hist})


# -------- fábrica de grafo --------
def create_graph() -> Tuple[Any, Deps]:
    """
    Construye grafo mínimo: agent -> tool.
    Currificamos deps en funciones internas para contentar al tipo de add_node.
    """
    deps = Deps()  # todos opcionales por defecto (model_name="test")

    async def _agent_action(state: GraphState) -> GraphState:
        return await node_agent(state, deps)

    async def _tool_action(state: GraphState) -> GraphState:
        return await node_tool(state, deps)

    g = StateGraph(GraphState)
    g.add_node("agent", _agent_action)
    g.add_node("tool", _tool_action)
    g.add_edge("agent", "tool")
    g.set_entry_point("agent")
    g.add_edge("tool", END)

    graph = g.compile()
    return graph, deps


# -------- ejecución con memoria --------
async def run_with_memory(
    graph_app: Any,
    deps: Deps,
    mm: Any,
    session_id: str,
    user_text: str,
    MAX_HISTORY: int = 15
) -> tuple[str, list[ModelMessage]]:
    history_raw = mm.load(session_id) if mm is not None else []
    history: list[ModelMessage] = ModelMessagesTypeAdapter.validate_python(history_raw or [])

    state = GraphState(session_id=session_id, user_input=user_text, history=history)
    final_dict = await graph_app.ainvoke(state)  # nodos ya cierran sobre deps
    final: GraphState = GraphState.model_validate(final_dict)

    reply = final.tool_output or final.agent_output or ""
    appended = final.history or [user_msg(user_text), assistant_msg(reply)]
    all_msgs = history + appended

    if mm is not None:
        await mm.save_from_result(session_id, all_msgs, MAX_HISTORY=MAX_HISTORY)

    return reply, all_msgs
