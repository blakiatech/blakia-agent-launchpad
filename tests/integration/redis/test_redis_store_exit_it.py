# tests/test_redis_store_exit.py
import fakeredis
from core.memory.redis_store import RedisWindowStore


def test_redis_window_store_set_empty_exits_cleanly():
    r = fakeredis.FakeRedis(decode_responses=True)
    s = RedisWindowStore(r)
    s.set("sid", [])
    assert r.llen("sid") == 0
