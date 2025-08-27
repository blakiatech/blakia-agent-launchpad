from core.memory import get_memory_store, memory_store, RedisWindowStore
from infrastructure.settings import settings


def _clear_redis_env(monkeypatch):
    for var in [
        "REDIS_URL",
        "REDIS_HOST",
        "REDIS_PORT",
        "REDIS_DB",
        "REDIS_PASSWORD",
    ]:
        monkeypatch.delenv(var, raising=False)


def test_get_memory_store_fallback_redis(monkeypatch):
    _clear_redis_env(monkeypatch)
    monkeypatch.setattr(settings, "memory_backend", "redis")
    store = get_memory_store()
    assert store is memory_store


def test_get_memory_store_fallback_combined(monkeypatch):
    _clear_redis_env(monkeypatch)
    monkeypatch.setattr(settings, "memory_backend", "combined")
    stores = get_memory_store()
    assert stores == [memory_store]


def test_get_memory_store_redis_with_url(monkeypatch):
    _clear_redis_env(monkeypatch)
    monkeypatch.setattr(settings, "memory_backend", "redis")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    store = get_memory_store()
    assert isinstance(store, RedisWindowStore)


def test_get_memory_store_combined_with_url(monkeypatch):
    _clear_redis_env(monkeypatch)
    monkeypatch.setattr(settings, "memory_backend", "combined")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    stores = get_memory_store()
    assert len(stores) == 2
    assert stores[0] is memory_store
    assert isinstance(stores[1], RedisWindowStore)
