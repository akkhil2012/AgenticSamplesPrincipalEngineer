import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import create_app
from demo import sample


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test.db"


@pytest.fixture
def app(db_path):
    return create_app(db_path)


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture
def registered(client):
    result = client.post("/control/agents", json=sample("register.json"))
    assert result.status_code == 201
    return client
