import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fastapi_sincrono.app import app
from fastapi_sincrono.database import get_session
from fastapi_sincrono.models import User, table_registry
from fastapi_sincrono.security import get_password_hash


@pytest.fixture
def client(session: Session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def user(session: Session):
    pwd = 'rextest01'
    user = User(
        username='Rex',
        email='TiRex@teste.com',
        password=get_password_hash(pwd),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = pwd  # Monkey patching para testes
    return user


@pytest.fixture
def user2(session: Session):
    user_2 = User(
        username='Duckssauro',
        email='Duckssauro@teste.com',
        password=get_password_hash('duckt01'),
    )
    session.add(user_2)
    session.commit()
    session.refresh(user_2)
    return user


@pytest.fixture
def token(client: TestClient, user: User):
    response = client.post(
        '/token',
        data={'username': user.username, 'password': user.clean_password},
    )
    return response.json()['access_token']
