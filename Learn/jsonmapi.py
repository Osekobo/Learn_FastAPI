from pydantic import BaseModel, EmailStr


class UserGetRegister (BaseModel):
    id: int
    name: str
    phone: str
    email: EmailStr


class UserPostRegister(BaseModel):
    name: str
    phone: str
    email: EmailStr
    password: str


class Token(BaseModel):
    token: str
    token_type: str
