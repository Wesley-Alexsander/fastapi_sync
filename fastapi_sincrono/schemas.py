from typing import List
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from fastapi_sincrono.models import TodoStatus


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserDB(UserSchema):
    id: int


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=0)


class FilterTodo(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoStatus | None = None


class TodoSchema(BaseModel):
    title: str
    description: str | None = None
    state: TodoStatus = TodoStatus.pending


class TodoPublic(TodoSchema):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TodoList(BaseModel):
    todos: List[TodoPublic]


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoStatus | None = None
