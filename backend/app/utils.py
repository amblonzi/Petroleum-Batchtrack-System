# backend/app/utils.py
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from .config import settings

# Password hashing
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto", argon2__rounds=2)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)