from pydantic_ai.tools import RunContext
from core.deps import Deps
from observability.langfuse.tracing import traced_tool


@traced_tool("dummy_tool")
async def dummy_tool(context: RunContext[Deps], payload: str = "") -> str:
    """Enviar una solicitud de soporte con una fecha específica."""

    return f"TOOL_OK: Has llamado a una tool. Payload: {payload}"

