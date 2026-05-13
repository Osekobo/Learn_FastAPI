from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://postgres:12039@localhost:5432/test"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# {
#   "name": "John Doe",
#   "phone": "0712345678",
#   "email": "john@example.com",
#   "password": "secret123"
# }

