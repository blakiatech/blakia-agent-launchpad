from fastapi.testclient import TestClient
from infrastructure.server import app

def test_health_and_metrics():
    c = TestClient(app)
    assert c.get("/health").status_code == 200
    assert c.get("/metrics").status_code == 200

