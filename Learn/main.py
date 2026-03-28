from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm
from jsonmap import UserGetRegister, UserPostRegister, Token, ProductGetMap, ProductPostMap, PurchaseGetMap, PurchasePostMap
from models import User, Product, Purchase
from myjwt import get_db, create_password_hash, verify_password, create_access_token, get_current_user
from datetime import timedelta
app = FastAPI()
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@app.post("/register", response_model=UserGetRegister, status_code=201)
def register(user: UserPostRegister, db: Session = Depends(get_db)):
    if db.scalars(select(User).where(User.email == user.email)):
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.scalars(select(User).where(User.phone == user.phone)):
        raise HTTPException(status_code=400, detail="Phone already registered")
    usr = User(name=user.name, phone=user.phone,
               email=user.email, password=create_password_hash(user.password))
    try:
        db.add(usr)
        db.commit()
        db.refresh(usr)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Registration failed")
    return usr


@app.post("/login", response_model=Token)
def login(data: OAuth2PasswordRequestForm, db: Session = Depends(get_db)):
    email = data.username.lower().strip()
    user = db.scalars(select(User).where(User.email == email))
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password", headers="WWW-Authenticate")
    token = create_access_token(data={"sub": user.email, "scope": "me items"}, expires_delta=timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return Token(token=token, token_type="bearer")


@app.get("/products", response_model=list[ProductGetMap])
def get_products(db: Session = Depends(get_db)):
    return db.scalars(select(Product)).all()


@app.post("/products", response_model=ProductGetMap, status_code=201)
def create_products(product: ProductPostMap, db: Session = Depends(get_db)):
    prod = Product(**product.model_dump())
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return prod


@app.get("/purchase", response_model=list[PurchaseGetMap])
def get_purchase(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.scalars(select(Purchase).where(Purchase.user_id == current_user.id)).all()


@app.post("/purchase", response_model=PurchaseGetMap, status_code=201)
def create_purchase(purchase: PurchasePostMap, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_purchase = Purchase(quantity=purchase.quantity,
                            product_id=purchase.product_id, user_id=current_user.id)
    db.add(new_purchase)
    db.commit()
    db.refresh(new_purchase)

    return new_purchase
