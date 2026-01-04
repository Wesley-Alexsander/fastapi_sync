from http import HTTPStatus


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
