import hashlib
from datetime import datetime, timedelta
from app.core.config import settings
from jose import jwt

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed_password: str):
    return hash_password(password) == hashed_password

def create_access_token(data: dict):
    data["exp"] = datetime.utcnow() + timedelta(
        minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict):
    data_copy = data.copy()
    data_copy["exp"] = datetime.utcnow() + timedelta(
        days = settings.REFRESH_TOKEN_EXPIRE_DAYS  
    )
    return jwt.encode(data_copy, settings.SECRET_KEY, algorithm=settings.ALGORITHM)