import json
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from src.auth.schemas import TokenFields
from src.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def encode_jwt(
        payload: dict,
        private_key: str = settings.auth.private_key,
        algorithm: str = settings.auth.ALGORITHM,
        expire_minutes: int = settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES,
        expire_timedelta: timedelta | None = None,
        jti: str | None = None,
) -> str:

    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update({
        TokenFields.TOKEN_EXPIRE_FIELD.value: int(expire.timestamp()),
        TokenFields.TOKEN_IAT_FIELD.value: int(now.timestamp()),
    })
    if jti is not None:
        to_encode.update({TokenFields.TOKEN_JTI_FIELD.value: jti})

    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )

    return encoded


def decode_jwt(
        token: str | bytes,
        public_key: str = settings.auth.public_key,
        algorithm: str = settings.auth.ALGORITHM,
) -> dict:
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decoded


def hash_password(password: str) -> str:
    """Хэширование пароля"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)
