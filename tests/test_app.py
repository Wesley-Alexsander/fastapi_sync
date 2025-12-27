from http import HTTPStatus


def test_read_root_say_hello(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK  # 200
    assert response.json() == {'message': 'Testando'}


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'Rex',
            'email': 'Rex@example.com',
            'password': '1234',
        },
    )
    assert response.status_code == HTTPStatus.CREATED  # 201
    assert response.json() == {
        'id': 1,
        'username': 'Rex',
        'email': 'Rex@example.com',
    }


def read_users(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK  # 200
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'username': 'Rex',
                'email': 'Rex@example.com',
            },
        ]
    }
