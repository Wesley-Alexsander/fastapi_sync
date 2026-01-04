from http import HTTPStatus


def test_read_root_say_hello(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK  # 200
    assert response.json() == {'message': 'Testando'}
