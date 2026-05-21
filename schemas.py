from pydantic import BaseModel, EmailStr


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
