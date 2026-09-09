from fastapi.testclient import TestClient

from src.v5.api.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == (
        "V5 Calibration Intelligence Platform"
    )

    assert data["version"] == "5.0.0"
    assert data["status"] == "running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_system_status():
    response = client.get("/system/status")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["api_version"] == "5.0.0"