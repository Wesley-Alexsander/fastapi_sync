from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_sincrono.database import get_session
from fastapi_sincrono.models import User
from fastapi_sincrono.schemas import Token
from fastapi_sincrono.security import (
    create_access_token,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])

AuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]
SessionUser = Annotated[Session, Depends(get_session)]


@router.post('/token', response_model=Token)
def login_for_acess_token(
    form_data: AuthForm,
    session: SessionUser,
):
    user = session.scalar(
        select(User).where(User.username == form_data.username)
    )

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect Username or password',
        )

    acess_token = create_access_token(data={'sub': user.username})

    return {'access_token': acess_token, 'token_type': 'bearer'}
