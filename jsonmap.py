from pydantic import BaseModel, EmailStr
from datetime import datetime


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


class PurchasePostMap(BaseModel):
    product_id: int
    quantity: float


class PurchaseGetMap(PurchasePostMap):
    id: int
    quantity: float
    product_id: int
    created_at: datetime
    updated_at: datetime


class SaleDetailsItem(BaseModel):
    product_id: int
    quantity: float


class SaleDetailsItem(BaseModel):
    product_id: int
    quantity: float


class SalePostMap(BaseModel):
    details: list[SaleDetailsItem]


class SaleGetMap(SalePostMap):
    id: int
    created_at: datetime
    updated_at: datetime


class TokenData(BaseModel):
    email: str | None = None
    scopes: list[str] = []
