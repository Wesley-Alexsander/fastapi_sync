import pytest
from fastapi.testclient import TestClient

from fastapi_sincrono.app import app


@pytest.fixture
def client():
    return TestClient(app)
