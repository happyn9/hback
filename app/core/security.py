# app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings


# Password hashing context
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


# =========================
# Password utilities
# =========================

def hash_password(password: str) -> str:
    """
    Hash a plain password using bcrypt_sha256.
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash.
    """
    return pwd_context.verify(password, hashed_password)


def hash_pin(pin: str):
    return pwd_context.hash(pin)

def verify_pin(pin: str, hashed: str):
    return pwd_context.verify(pin, hashed)


# =========================
# JWT utilities
# =========================

def create_access_token(
    data: Dict[str, Any],
    remember_me: bool = False
) -> str:
    """
    Create a JWT access token.
    """

    if remember_me:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REMEMBER_ME_DAYS
        )
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = data.copy()
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT access token.
    Returns payload if valid, otherwise None.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None