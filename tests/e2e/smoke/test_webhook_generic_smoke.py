from fastapi.testclient import TestClient
from infrastructure.server import app

def test_generic_webhook_smoke():
    c = TestClient(app)
    r = c.post(
        "/webhooks/generic/generic-webhook",
        headers={"x-api-key": "dummy"},
        json={"session_id": "t1", "message": "hola"},
    )
    assert r.status_code in (200, 401)  # según tengas verificación activada

