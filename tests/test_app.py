from http import HTTPStatus

from fastapi.testclient import TestClient

from fastapi_sincrono.app import app


def test_read_root_say_hello():
    client = TestClient(app)  # Arrange (organização)
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK  # 200
    assert response.json() == {'message': 'Testando'}
