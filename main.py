from models import User
from fastapi import FastAPI, Depends, HTTPException, status
from schemas import UserGetRegister, UserPostRegister, UserGetLogin, UserPostLogin
from sqlalchemy.orm import Session
from sqlalchemy import select
from utils import (get_db, create_access_token,
                   get_password_hash, verify_password)
from datetime import timedelta
ACCESS = 30
app = FastAPI()


@app.get("/")
def home():
    return {"Version": "1"}


@app.post("/register", response_model=UserGetRegister, status_code=201)
def register(user: UserPostRegister, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == user.email)):
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(name=user.name, phone=user.phone,
                    email=user.email, password=get_password_hash(user.password))
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="User registration failed")
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS))
    # return {
    #     "id": user.user_id
    # }
    return new_user


@app.post("/login", response_model=UserGetLogin)
def login(data: UserPostLogin, db: Session = Depends(get_db)):
    email = data.email.lower().strip()
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    access_token = create_access_token(
        data={"sub": data.email}, expires_delta=timedelta(minutes=ACCESS))
    return UserGetLogin(access_token=access_token, token_type="bearer")
