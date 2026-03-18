from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, create_engine, String

DATABASE_URL = "postgresql://postgres:12039@localhost:5432/fast_api"
engine = create_engine(DATABASE_URL)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
