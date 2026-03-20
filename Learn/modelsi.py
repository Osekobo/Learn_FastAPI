from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from datetime import datetime


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column()
    phone: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    created_on: Mapped[datetime] = mapped_column()
    updated_on: Mapped[datetime] = mapped_column()
