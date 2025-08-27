# tests/test_memory_factory_edges.py
from core.memory import get_memory_store, InMemoryHistory, RedisWindowStore


def test_get_memory_store_redis_without_env(monkeypatch):
    for k in ["REDIS_URL", "REDIS_HOST", "REDIS_PORT", "REDIS_DB", "REDIS_PASSWORD"]:
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv(
        "MEMORY_BACKEND", "redis", prepend=False
    )  # si settings usa esto internamente, ajusta
    # si settings.memory_backend se toma de infrastructure.settings.settings, forza:
    from infrastructure.settings import settings as cfg

    monkeypatch.setattr(cfg, "memory_backend", "redis", raising=False)

    store = get_memory_store()
    assert isinstance(store, InMemoryHistory)


def test_get_memory_store_combined_without_env(monkeypatch):
    for k in ["REDIS_URL", "REDIS_HOST", "REDIS_PORT", "REDIS_DB", "REDIS_PASSWORD"]:
        monkeypatch.delenv(k, raising=False)
    from infrastructure.settings import settings as cfg

    monkeypatch.setattr(cfg, "memory_backend", "combined", raising=False)

    stores = get_memory_store()
    assert (
        isinstance(stores, list)
        and any(isinstance(s, InMemoryHistory) for s in stores)
        and not any(isinstance(s, RedisWindowStore) for s in stores)
    )
