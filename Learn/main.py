from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from jsonmapi import GetRegister, PostRegister, Token
from modelsi import User
from myjwti import get_db, verify_password, create_access_token
from datetime import timedelta
app = FastAPI()
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@app.post("/register", response_model=GetRegister, status_code=201)
def register(user: PostRegister, db: Session = Depends(get_db)):

    if db.scalar(select(User).where(User.email == user.email)):
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.scalar(select(User).where(User.phone == user.phone)):
        raise HTTPException(status_code=400, detail="Phone already registered")
    new_user = User(name=user.name, phone=user.phone,
                    email=user.email, password=user.password)
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Registration failed")
    return new_user


@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = form_data.lower().strip()
    db_user = db.scalar(select(User).where(User.email == email))
    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password", headers={"WWW_Authenticate": "Bearer"})
    access_token = create_access_token(
        data={"sub": db_user.email, "scope": "me items"}, expires_delta=timedelta(ACCESS_TOKEN_EXPIRE_MINUTES))
    return Token(access_token=access_token, token_type="bearer")
