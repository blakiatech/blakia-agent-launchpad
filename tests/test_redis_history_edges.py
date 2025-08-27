import fakeredis
from core.memory.redis_history import RedisHistory
from core.memory.codec import dumps_list
from pydantic_ai.messages import ModelRequest, UserPromptPart


def test_redis_history_save_noop_and_load_valid_bytes():
    r = fakeredis.FakeRedis(decode_responses=False)
    h = RedisHistory("S", r)
    h._save([])  # early exit

    msg = ModelRequest(parts=[UserPromptPart("hola")])
    payload = dumps_list([msg])[0]
    r.rpush("S", payload.encode("utf-8"))

    msgs = h._load()
    assert len(msgs) == 1 and isinstance(msgs[0], ModelRequest)


def test_redis_history_ignores_other_sid_on_get_set_clear():
    r = fakeredis.FakeRedis(decode_responses=True)
    h = RedisHistory("A", r)
    # get con sid distinto
    assert h.get("B") == []
    # set con sid distinto no debe escribir
    h.set("B", [ModelRequest(parts=[UserPromptPart("x")])])
    assert r.llen("A") == 0 and r.llen("B") == 0
    # clear con sid distinto no borra nada (no peta)
    h.clear("B")
