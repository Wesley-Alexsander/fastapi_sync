from http import HTTPStatus

from freezegun import freeze_time


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.username,
            'password': user.clean_password,
        },
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['access_token']
    assert token['token_type'] == 'bearer'


def test_get_token_with_incorrect_credentials_should_return_401(client):
    response = client.post(
        '/auth/token',
        data={
            'username': 'wronguser',
            'password': 'wrongpassword',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect Username or password'}


def test_token_expiration(client, user):
    with freeze_time('2024-01-01 12:00:00'):
        response = client.post(
            '/auth/token',
            data={
                'username': user.username,
                'password': user.clean_password,
            },
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    # Avançar o tempo além do tempo de expiração do token
    with freeze_time('2024-01-01 13:01:00'):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'Duckssauro',
                'email': user.email,
                'password': user.clean_password,
            },
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_wrong_password(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.username,
            'password': 'wrongpassword',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect Username or password'}


def test_token_wrong_username(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': 'wronguser',
            'password': user.clean_password,
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect Username or password'}
