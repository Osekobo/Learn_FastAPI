from pydantic import BaseModel, EmailStr
from datetime import date


class UserGetRegister(BaseModel):
    id: int
    name: str
    phone: str
    email: EmailStr
    access_token: str
    token_type: str


class UserPostRegister(BaseModel):
    name: str
    phone: str
    email: EmailStr
    password: str


class UserGetLogin(BaseModel):
    access_token: str
    token_type: str


class UserPostLogin(BaseModel):
    email: EmailStr
    password: str


class GetForm(BaseModel):
    id: int
    name: str
    price: int
    category: str
    date: date
    income: str


class PostForm(BaseModel):
    name: str
    price: int
    category: str
    date: date
    income: str
