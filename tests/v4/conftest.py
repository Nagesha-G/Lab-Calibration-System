import pytest
from fastapi.testclient import TestClient

from src.v4.api import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client