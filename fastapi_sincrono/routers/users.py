from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi_sincrono.database import get_session
from fastapi_sincrono.models import User
from fastapi_sincrono.schemas import (
    FilterPage,
    Message,
    UserList,
    UserPublic,
    UserSchema,
)
from fastapi_sincrono.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix='/users', tags=['users'])

SessionUser = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
FilterPageParams = Annotated[FilterPage, Query()]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: SessionUser):
    db_user = session.scalar(
        select(User).where(
            or_(User.email == user.email, User.username == user.username)
        )
    )

    if db_user:
        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email Already Exists',
            )

        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username Already Exists',
            )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
def get_users(session: SessionUser, fiter_page: FilterPageParams):
    user_list = session.scalars(
        select(User).limit(fiter_page.limit).offset(fiter_page.skip)
    ).all()
    return {'users': user_list}


@router.get('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def get_user(user_id: int, session: SessionUser):
    user = session.scalar(select(User).where(User.id == user_id))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User Not Found'
        )

    return user


@router.put('/{user_id}', response_model=UserPublic)
def update_users(
    user_id: int,
    user: UserSchema,
    session: SessionUser,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Not enough permissions',
        )

    try:
        current_user.email = user.email
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)
        session.commit()
        session.refresh(current_user)

        return current_user

    except IntegrityError as e:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        ) from e


@router.delete('/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_user(
    user_id: int,
    session: SessionUser,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Not enough permissions',
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted'}
