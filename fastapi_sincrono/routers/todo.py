from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_sincrono.database import get_session
from fastapi_sincrono.models import Todo, User
from fastapi_sincrono.schemas import (
    FilterPage,
    FilterTodo,
    Message,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from fastapi_sincrono.security import get_current_user

router = APIRouter(prefix='/todo', tags=['todo'])
SessionUser = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
TodoFilterParams = Annotated[FilterTodo, Depends()]
FilterPageParams = Annotated[FilterPage, Depends()]


@router.post('/', response_model=TodoPublic)
def create_todo(
    todo: TodoSchema, session: SessionUser, current_user: CurrentUser
):
    todo_db = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=current_user.id,
    )

    session.add(todo_db)
    session.commit()
    session.refresh(todo_db)

    return todo_db


@router.get('/', response_model=TodoList)
def list_todos(
    session: SessionUser,
    current_user: CurrentUser,
    filter_params: TodoFilterParams,
    pagination: FilterPageParams,
):
    query = select(Todo).where(Todo.user_id == current_user.id)

    if filter_params.title:
        query = query.filter(Todo.title.contains(filter_params.title))
    if filter_params.description:
        query = query.filter(
            Todo.description.contains(filter_params.description)
        )
    if filter_params.state:
        query = query.filter(Todo.state == filter_params.state)

    todo_db = session.scalars(
        query.offset(pagination.skip).limit(pagination.limit)
    ).all()

    return {'todos': todo_db}


@router.delete('/{todo_id}', response_model=Message)
def delete_todo(
    session: SessionUser,
    current_user: CurrentUser,
    todo_id: int,
):
    todo = session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    )
    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Todo not found'
        )

    session.delete(todo)
    session.commit()
    return {'message': 'Todo deleted successfully'}


@router.patch('/{todo_id}', response_model=TodoPublic)
def update_todo(
    todo_id: int,
    session: SessionUser,
    current_user: CurrentUser,
    todo_update: TodoUpdate,
):
    db_todo = session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Todo not found'
        )

    for key, value in todo_update.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo
