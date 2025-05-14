from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum as PyEnum
from datetime import datetime


class UserRole(str, PyEnum):
    normal = "normal"
    admin = "admin"
    editor = "editor"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.admin


class SetPassword(BaseModel):
    email: EmailStr
    token: str
    new_password: str


class ShowUser(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class UserUpdateRole(BaseModel):
    user_id: int
    new_role: UserRole
