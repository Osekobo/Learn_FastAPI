# https://chatgpt.com/s/t_6a022a195e7c8191a154912ad410cdd7
# get_db, get_password_hash, verify_password, create_access_token, get_current_user
from database import SessionLocal
from models import User
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from fastapi.security import SecurityScopes, OAuth2PasswordBearer
import jwt
from schemas import TokenData
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy import select

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login",
    scopes={
        "me": "Read information about the current user",
        "items": "Read items",
    },
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Hash password
def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_email(db: Session, email: str):
    return db.scalar(select(User).where(User.email == email))

# create access token


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    authenticate_value = "Bearer"
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        scope_str: str = payload.get("scope", "")
        token_scopes = scope_str.split()

        token_data = TokenData(email=email, scopes=token_scopes)
    except (InvalidTokenError, ValidationError):
        raise credentials_exception

    user = get_user_by_email(db, token_data.email)
    if user is None:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    # print("Token Scopes:", token_data.scopes)
    # print("Required Scopes:", security_scopes.scopes)

    return user
