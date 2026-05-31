from database import Base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)


class Form(Base):
    __tablename__ = "formdata"
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    income = Column(String, nullable=False)
