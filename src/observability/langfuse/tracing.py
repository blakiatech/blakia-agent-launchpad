# observability/langfuse/tracing.py
from opentelemetry import trace
from functools import wraps
from observability.langfuse.configure import configure_langfuse

tracer = configure_langfuse()


def traced_tool(tool_name: str):
    """
    Decorador para trazar la ejecución de tools en Pydantic AI.

    Args:
        tool_name: Nombre identificativo de la tool (aparece en Langfuse/OTEL).
    """

    def decorator(func):
        @wraps(func)  # 🔹 Esto mantiene el nombre original y evita el conflicto
        async def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(f"tool:{tool_name}") as span:
                span.set_attribute("tool.args", str(args))
                span.set_attribute("tool.kwargs", str(kwargs))
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("tool.result", str(result))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    raise

        return wrapper

    return decorator
