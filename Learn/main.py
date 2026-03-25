from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm
from jsonmap import UserGetRegister, UserPostRegister, Token, ProductGetMap, ProductPostMap
from models import User, Product
from myjwt import get_db, create_password_hash, verify_password, create_access_token, get_current_user
from datetime import timedelta
app = FastAPI()
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@app.post("/register", response_model=UserGetRegister, status_code=201)
def register(user: UserPostRegister, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == user.email)):
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.scalar(select(User).where(User.phone == user.phone)):
        raise HTTPException(status_code=400, detail="Phone already exists")
    usr = User(name=user.name, phone=user.phone,
               email=user.email, password=create_password_hash(user.password))
    try:
        db.add(usr)
        db.commit()
        db.refresh(usr)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=501, detail="Registration failed")
    return usr


@app.post("/login", response_model=Token)
def login(data: OAuth2PasswordRequestForm, db: Session = Depends(get_db)):
    email = data.username.lower().strip()
    usr = db.scalar(select(User).where(User.email == email))
    if not usr or not verify_password(data.password, usr.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password", headers={"WWW-Authenticate": "Bearer"})

    token = create_access_token(
        data={"sub": usr.email, "scope": "me items"}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),)

    return Token(token=token, token_type="bearer")


@app.get("/products", response_model=list[ProductGetMap])
def get_products(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Product)).all()


@app.post("/products", response_model=ProductGetMap, status_code=201)
def create_product(product: ProductPostMap, db: Session = Depends(get_db), curent_user: User = Depends(get_current_user)):
    model = Product(**product.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return model
