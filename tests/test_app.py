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


def test_read_users(client):
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


def test_read_users_by_id(client):
    response = client.get('/users/1')
    assert response.status_code == HTTPStatus.OK  # 200
    assert response.json() == {
        'id': 1,
        'username': 'Rex',
        'email': 'Rex@example.com',
    }


def test_update_user(client):
    response = client.put(
        '/users/1',
        json={
            'id': 1,
            'username': 'TIRex',
            'email': 'TIRex@example.com',
            'password': '1234',
        },
    )

    assert response.json() == {
        'id': 1,
        'username': 'TIRex',
        'email': 'TIRex@example.com',
    }


def test_update_user_that_not_exist(client):
    response = client.put(
        '/users/3',
        json={
            'id': 3,
            'username': 'TIRex',
            'email': 'TIRex@example.com',
            'password': '1234',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND  # 404
    assert response.json() == {'detail': 'User Not Found'}


def test_delete_user(client):
    response = client.delete('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_that_not_exist(client):
    response = client.delete('/users/2')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User Not Found'}
