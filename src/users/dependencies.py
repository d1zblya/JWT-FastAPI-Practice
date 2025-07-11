import uuid
from typing import Annotated
from loguru import logger

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from src.auth import utils as auth_utils
from src.auth.schemas import TokenFields
from src.exceptions.user import UserNotFound
from src.users.schemas import UserOut
from src.users.service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserOut:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = auth_utils.decode_jwt(token)
        user_id = uuid.UUID(payload.get(TokenFields.TOKEN_SUB_FIELD.value))
        if user_id is None:
            logger.error(f"user_id not found in the token")
            raise credentials_exception
    except InvalidTokenError:
        logger.error(f"Invalid token")
        raise credentials_exception

    user = await UserService.get_user(user_id)
    if user is None:
        msg = f"User not found"
        logger.error(msg)
        raise UserNotFound(msg)

    return UserOut.model_validate(user)

