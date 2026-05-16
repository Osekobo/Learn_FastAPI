from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas import UserGetRegister, UserPostRegister, Token
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import User
from utils import (get_db,
                   get_password_hash, verify_password, create_access_token)
ACCESS_TOKEN_EXPIRE_MINUTES = 30
app = FastAPI()


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
