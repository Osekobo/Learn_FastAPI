from models import User, Form
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
# GetItem, PostItem, GetList, PostList
from schemas import UserGetRegister, UserPostLogin, UserGetLogin, UserPostRegister, GetForm, PostForm, GetExpenseSchema
from utils import (get_db, verify_password,
                   get_password_hash, create_access_token)
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import timedelta
from database import Base, engine
import models

Base.metadata.create_all(bind=engine)
# Base.metadata.drop_all(bind=engine)
ACCESS = 30
app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"Version": "1.0"}


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
    return {
        "id": new_user.id,
        "name": new_user.name,
        "phone": new_user.phone,
        "email": new_user.email,
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.post("/login", response_model=UserGetLogin)
def login(data: UserPostLogin, db: Session = Depends(get_db)):
    email = data.email.lower().strip()
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password")
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS))
    # return UserGetLogin(access_token=access_token, token_type="bearer")
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/expenseform", response_model=list[GetForm])
def get_expense(db: Session = Depends(get_db)):
    expenses = db.scalars(select(Form)).all()
    return expenses


@app.post("/expenseform", response_model=GetForm)
def post_expense(data: PostForm, db: Session = Depends(get_db)):
    info = data.name.lower().strip()
    # ensere all fields are set
    if db.scalar(select(Form).where(Form.name == info)):
        raise HTTPException(detail="Expense already added", status_code=400)
    new_data = Form(name=data.name, price=data.price,
                    category=data.category, date=data.date, income=data.income)
    try:
        db.add(new_data)
        db.commit()
        db.refresh(new_data)
    except:
        db.rollback()
        raise HTTPException(
            detail="Error adding expense form data", status_code=400)
    return new_data


@app.delete("/expenseform/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.scalar(select(Form).where(Form.id == expense_id))
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return {"messagw": "Expense deleted successfully"}


@app.put("/expenseform/{id}")
def update_expense(id: int, expense: GetExpenseSchema):
    # update logic here
    return {"message": "updated"}
