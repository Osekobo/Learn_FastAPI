from pydantic import BaseModel, EmailStr
# UserPostRegister, Token, UserGetRegister, ProductGetMap, ProductPostMap, PurchaseGetMap, PurchasePostMap, SaleGetMap, SalePostMap
# from decimal import Decimal


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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
    scopes: list[str] = []
    # scopes: list[str] = Field(default_factory=list)


class ProductGetMap(BaseModel):
    id: int
    name: str
    buying_price: float  # Decimal
    selling_price: float  # Decimal
    amount: int

    # class Config:
    # from_attributes = True


class ProductPostMap(BaseModel):
    name: str
    buying_price: float
    selling_price: float
    amount: int


# class PurchaseGetMap(BaseModel):
#     id: int
#     quantity: int
#     total_cost: float


# class PurchasePostMap(BaseModel):
#     product_id: int
#     quantity: int
#     total_cost: float


class SaleGetMap(BaseModel):
    id: int
    product_id: int
    quantity: int
    total_cost: float


class SalePostMap(BaseModel):
    product_id: int
    quantity: int
    total_cost: float
