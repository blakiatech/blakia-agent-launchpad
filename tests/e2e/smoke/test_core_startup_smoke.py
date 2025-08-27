# tests/test_smoke_core.py
import asyncio
import httpx
import fakeredis

from core.graph import create_graph, run_with_memory
from core.deps import Deps


class DummyMM:
    """Memory manager mínimo para el smoke: no persiste nada."""

    def load(self, session_id: str):
        return []

    async def save_from_result(self, session_id: str, messages, MAX_HISTORY: int = 15):
        return None


async def _ainvoke(graph, deps):
    mm = DummyMM()
    return await run_with_memory(
        graph_app=graph,
        deps=deps,
        mm=mm,
        session_id="smoke",
        user_text="Hola hola!!!",
    )


def test_smoke_core():
    """Importa core, crea grafo y hace una query end-to-end sin explotar."""
    graph, deps = create_graph()

    # Endpoints reales NO: metemos clientes “seguros” para el smoke
    fake_redis = fakeredis.FakeRedis(decode_responses=True)

    async def _noop_send(_msg):
        return None

    deps = Deps(
        http=httpx.AsyncClient(),
        redis=fake_redis,  # evita redis real
        openai_api_key="dummy",  # el router está parcheado en tus tests
        telegram_bot_token="dummy",
        empresas_api_token="dummy",
        send_catalog_message=_noop_send,  # firma: async (dict) -> None
    )

    result, history = asyncio.run(_ainvoke(graph, deps))

    assert isinstance(result, str)
    assert isinstance(history, list)
    # no validamos contenido; solo que corre sin excepciones
