from pydantic import BaseModel, EmailStr


class UserGetRegister(BaseModel):
    id: int
    name: str
    phone: str
    email: EmailStr


class UserPostRegister(BaseModel):
    name: str
    phone: str
    email: EmailStr
    password: str


class UserPostLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class ProductPostMap(BaseModel):
    name: str
    buying_price: float
    selling_price: float
    model: str
    year: int
    condition: str
    fuel: str
    # created_at: str


class ProductGetMap(ProductPostMap):
    id: int
