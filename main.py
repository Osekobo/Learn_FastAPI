# ruff format .
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select
# PurchaseGetMap, PurchasePostMap,
from schemas import UserPostRegister, Token, UserGetRegister, ProductGetMap, ProductPostMap, SaleGetMap, SalePostMap
from utils import (get_db, get_password_hash,
                   verify_password, create_access_token, get_current_user)
from models import User, Product, Sale  # Purchase
from datetime import timedelta
from database import engine, Base
ACCESS_TOKEN_EXPIRE_MINUTES = 30

Base.metadata.create_all(bind=engine)
# Base.metadata.drop_all(bind=engine)
app = FastAPI()


@app.get("/")
def home():
    return {"Fast_API": "Version 01"}


@app.post("/register", response_model=UserGetRegister, status_code=201)
def register(user: UserPostRegister, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == user.email)):
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.scalar(select(User).where(User.phone == user.phone)):
        raise HTTPException(status_code=400, detail="Phone already registered")
    new_user = User(name=user.name, phone=user.phone,
                    email=user.email, password=get_password_hash(user.password))
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Registration Failed")
    return new_user


@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = form_data.username.lower().strip()
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or Password", headers={"WWW-Authenticate": "Bearer"})
    access_token = create_access_token(
        data={"sub": user.email, "scope": "me items"}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return Token(access_token=access_token, token_type="bearer")


@app.get("/products", response_model=list[ProductGetMap])
def get_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # return db.scalars(select(Product)).all()
    return db.query(Product).all()


@app.post("/products", response_model=ProductGetMap, status_code=201)
def create_product(product: ProductPostMap, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # model = Product(**product.model_dump())
    new_prod = Product(name=product.name, buying_price=product.buying_price,
                       selling_price=product.selling_price, amount=product.amount)
    db.add(new_prod)
    db.commit()
    db.refresh(new_prod)
    return new_prod


# @app.get("/purchases", response_model=list[PurchaseGetMap])
# def get_purchases(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     return db.query(Purchase).all()
#     # return db.scalars(select(Purchase).where(Purchase.user_id == current_user.id)).all()


# @app.post("/purchases", response_model=PurchaseGetMap, status_code=201)
# def create_purchase(purchase: PurchasePostMap, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     new_purchase = Purchase(quantity=purchase.quantity,
#                             # user_id=current_user.id)
#                             product_id=purchase.product_id, total_cost=purchase.total_cost)
#     db.add(new_purchase)
#     db.commit()
#     db.refresh(new_purchase)
#     return new_purchase


@app.get("/sales", response_model=list[SaleGetMap])
def get_sales(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Sale).all()
    # return db.query(Sale).filter(Sale.user_id == current_user.id).all()
    # return db.scalars(select(Sale).where(Sale.user_id == current_user.id)).all()


@app.post("/sales", response_model=SaleGetMap, status_code=201)
def create_sale(sale: SalePostMap, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_sale = Sale(product_id=sale.product_id, quantity=sale.quantity,
                    total_cost=sale.total_cost)
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)
    return new_sale

# [
#   {
#     "name": "Nike Air Force 1",
#     "buying_price": 8500,
#     "selling_price": 12000
#   },
#   {
#     "name": "Adidas Samba",
#     "buying_price": 7000,
#     "selling_price": 10500
#   },
#   {
#     "name": "Puma RS-X",
#     "buying_price": 6500,
#     "selling_price": 9800
#   },
#   {
#     "name": "New Balance 550",
#     "buying_price": 9000,
#     "selling_price": 13500
#   },
#   {
#     "name": "Converse Chuck Taylor",
#     "buying_price": 4000,
#     "selling_price": 6500
#   },
#   {
#     "name": "Vans Old Skool",
#     "buying_price": 5000,
#     "selling_price": 7800
#   },
#   {
#     "name": "Jordan 1 Mid",
#     "buying_price": 11000,
#     "selling_price": 16000
#   },
#   {
#     "name": "Reebok Club C 85",
#     "buying_price": 4800,
#     "selling_price": 7200
#   },
#   {
#     "name": "Asics Gel-Lyte III",
#     "buying_price": 7500,
#     "selling_price": 11200
#   },
#   {
#     "name": "Under Armour Curry Flow",
#     "buying_price": 9500,
#     "selling_price": 14500
#   }
# ]
