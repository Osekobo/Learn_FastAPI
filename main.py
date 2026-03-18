from fastapi import FastAPI, Depends, HTTPException
from jsonmap import UserGetRegister, UserPostRegister
from sqlalchemy.orm import Session
from models import User
from sqlalchemy import select
from myjwt import (get_db, get_password_hash)
app = FastAPI()


@app.get("/")
def home():
    return {"Duka FastAPI": "Version 1.0"}


@app.post("/register", response_model=UserGetRegister)
def register(user: UserPostRegister, db: Session = Depends(get_db)):

    if db.scalar(select(User).where(User.email == user.email)):
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.scalar(select(User).where(User.phone == user.phone)):
        raise HTTPException(status_code=400, detail="Phone already registered")

    new_user = User(name=user.name, phone=user.phone,
                    email=user.email, password=get_password_hash(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# uvicorn main:app --reload
