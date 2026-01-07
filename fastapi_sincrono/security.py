from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode

# from jwt.exceptions import PyJWTError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_sincrono.database import get_session
from fastapi_sincrono.models import User
from fastapi_sincrono.settings import Settings

pwd_context = PasswordHash.recommended()
settings = Settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})
    emcoded_jwt = encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return emcoded_jwt


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
):
    credencials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        decoded_token = decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        payload_username = decoded_token.get('sub')
        if not payload_username:
            raise credencials_exception
    except DecodeError as e:
        raise credencials_exception from e
    except ExpiredSignatureError as e:
        raise credencials_exception from e

    user_db = session.scalar(
        select(User).where(User.username == payload_username)
    )

    if not user_db:
        raise credencials_exception

    return user_db
