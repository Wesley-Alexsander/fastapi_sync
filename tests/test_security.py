from http import HTTPStatus

from jwt import decode

from fastapi_sincrono.security import create_access_token


def test_create_access_token(settings):
    data = {'sub': 'testuser'}
    token = create_access_token(data)
    result = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert result['sub'] == data['sub']
    assert result['exp']


def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_user_without_subject(client):
    token_without_sub = create_access_token(data={})
    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token_without_sub}'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_inexistent_user_token(client):
    data = {'sub': 'nonexistentuser'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
