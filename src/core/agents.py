# src/core/agents.py
from __future__ import annotations

from typing import Optional
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from infrastructure.settings import settings
from core.deps import Deps
from core.tools.dummy import dummy_tool
from core.memory.processors import keep_recent_messages

Agent.instrument_all()

SYSTEM_PROMPT = """
Eres un agente de ejemplo (plantilla). Responde de forma breve y neutral.
Si procede, puedes llamar a herramientas (tools). No inventes información.
"""

def _build_llm() -> OpenAIChatModel:
    return OpenAIChatModel(
        "gpt-4.1-mini",
        provider=OpenAIProvider(api_key=settings.openai_api_key),
    )

MAX_HISTORY = 15


def create_agent(model: Optional[OpenAIChatModel] = None) -> Agent[Deps, str]:
    """Permite inyectar un modelo OpenAI ya creado; si no, construye uno por defecto."""
    llm = model or _build_llm()
    agent = Agent(
        model=llm,
        system_prompt=SYSTEM_PROMPT,
        instrument=True,
        history_processors=[keep_recent_messages],
        deps_type=Deps,
        tools=[dummy_tool],
    )
    return agent
