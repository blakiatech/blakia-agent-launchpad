"""Processor for message cleaning"""

from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    UserPromptPart,
    ToolCallPart,
    ToolReturnPart,
    RetryPromptPart,  # <-- importa estos
)
from typing import List, Sequence

async def keep_recent_messages(messages: List[ModelMessage], MAX_HISTORY: int = 15) -> List[ModelMessage]:
    return messages[-MAX_HISTORY:] if len(messages) > MAX_HISTORY else messages

def strip_tool_traffic(messages: Sequence[ModelMessage]) -> list[ModelMessage]:
    cleaned: list[ModelMessage] = []
    for m in messages:
        if isinstance(m, ModelResponse):
            if any(isinstance(p, ToolCallPart) for p in m.parts):
                continue
            cleaned.append(m)
        elif isinstance(m, ModelRequest):
            pruned_parts: list[
                SystemPromptPart | UserPromptPart | ToolReturnPart | RetryPromptPart
            ] = [
                p for p in m.parts if isinstance(p, (SystemPromptPart, UserPromptPart))
            ]
            if pruned_parts:
                cleaned.append(ModelRequest(parts=pruned_parts))
    return cleaned
