# cordobai/core/memory/__init__.py
from __future__ import annotations
import os
from typing import List, Optional
from redis import Redis

from infrastructure.settings import settings
from .in_memory import InMemoryHistory, memory_store
from .manager import HistoryStore
from .redis_store import RedisWindowStore


def _env_str(key: str, default: str = "") -> str:
    v = os.getenv(key)
    return v if v is not None else default


def _env_int(key: str, default: int = 0) -> int:
    v = os.getenv(key)
    try:
        return int(v) if v is not None else default
    except ValueError:
        return default


def _build_redis_client() -> Optional[Redis]:
    url = os.getenv("REDIS_URL")
    if url:
        return Redis.from_url(url)
    host = _env_str("REDIS_HOST", "")
    port = _env_int("REDIS_PORT", 6379)
    db = _env_int("REDIS_DB", 0)
    password = os.getenv("REDIS_PASSWORD")  # Optional[str]

    if host:
        return Redis(
            host=host, port=port, db=db, password=password, decode_responses=True
        )
    return None


def get_memory_store() -> HistoryStore | list[HistoryStore] | None:
    """
    Devuelve la(s) store(s) de memoria según settings.memory_backend:
    - 'in_memory'  -> InMemoryHistory
    - 'redis'      -> RedisWindowStore si hay envs, si no, fallback a InMemoryHistory
    - 'combined'   -> [InMemoryHistory, (RedisWindowStore si hay envs)]
    """
    backend = getattr(settings, "memory_backend", "in_memory")
    client = _build_redis_client()

    if backend == "redis":
        return RedisWindowStore(client) if client else memory_store

    if backend == "combined":
        stores: List[HistoryStore] = [memory_store]
        if client:
            stores.append(RedisWindowStore(client))
        return stores

    return memory_store


__all__ = [
    "get_memory_store",
    "InMemoryHistory",
    "RedisWindowStore",
    "memory_store",
]
