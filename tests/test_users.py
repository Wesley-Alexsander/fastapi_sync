from http import HTTPStatus

from fastapi_sincrono.schemas import UserPublic


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
            'username': user.username,
            'email': user.email,
            'password': user.clean_password,
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
            'username': user.username,
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


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'TIRex',
            'email': 'TIRex@example.com',
            'password': '1234',
            'id': user.id,
        },
    )

    assert response.json() == {
        'id': 1,
        'username': 'TIRex',
        'email': 'TIRex@example.com',
    }


def test_update_user_when_email_already_exists_should_return_409(
    client, user, other_user, token
):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': user.username,
            'email': other_user.email,
            'password': user.clean_password,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or Email already exists'}


def test_update_user_when_not_owner_should_return_403(
    client, other_user, token
):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},  # o token do user 1
        json={
            'username': other_user.username,
            'email': other_user.email,
            'password': other_user.clean_password,
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN  # 403
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK

    response = client.get(f'/users/{user.id}')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user_when_not_owner_should_return_403(
    client, other_user, token
):
    response = client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}
