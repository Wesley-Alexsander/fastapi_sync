from http import HTTPStatus

from fastapi_sincrono.schemas import UserPublic


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


def test_create_user_when_email_already_exists_should_return_400(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'triceratops',
            'email': 'TiRex@teste.com',
            'password': '1234',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email Already Exists'}


def test_create_user_when_username_already_exists_should_return_400(
    client, user
):
    response = client.post(
        '/users/',
        json={
            'username': 'Rex',
            'email': 'Duckssauro@teste.com',
            'password': '1234',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username Already Exists'}


def test_read_users(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_list(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')

    assert 'password' not in response.json()
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_read_users_by_id(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK  # 200
    assert response.json() == user_schema


def test_update_user(client, user):
    response = client.put(
        '/users/1',
        json={
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


def test_update_user_when_email_already_exists_should_return_409(
    client, user, user2
):
    response = client.put(
        '/users/1',
        json={
            'username': 'TIRex',
            'email': 'Duckssauro@teste.com',
            'password': '1234',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or Email already exists'}


def test_update_user_when_user_not_exists_should_return_404(client):
    response = client.put(
        '/users/3',
        json={
            'username': 'TIRex',
            'email': 'TIRex@example.com',
            'password': '1234',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND  # 404
    assert response.json() == {'detail': 'User Not Found'}


def test_delete_user(client, user):
    response = client.delete(f'/users/{user.id}')
    assert response.status_code == HTTPStatus.OK

    response = client.get(f'/users/{user.id}')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user_when_user_not_exist(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User Not Found'}
