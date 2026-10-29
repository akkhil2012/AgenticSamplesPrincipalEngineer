import pytest
from fastapi.testclient import TestClient
from src.main import create_app
from src.config import Settings


@pytest.fixture
def settings(tmp_path):
    return Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}", rate_limit=1000)


@pytest.fixture
def app(settings):
    return create_app(settings)


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def manager():
    return {"Authorization": "Bearer demo-manager-a"}


@pytest.fixture
def approver():
    return {"Authorization": "Bearer demo-approver-a"}


def create(
    client,
    manager,
    message="Identify eligible customers and prepare a premium upgrade campaign.",
    key="test-request-001",
):
    response = client.post(
        "/agentic/requests", headers=manager, json={"message": message, "idempotency_key": key}
    )
    assert response.status_code == 200, response.text
    return response.json()
