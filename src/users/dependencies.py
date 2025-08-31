import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import utils as auth_utils
from src.auth.schemas import TokenFields
from src.database.session import get_session
from src.exceptions.exception_auth import PayloadError
from src.exceptions.exception_user import UserNotFound
from src.users.schemas import UserOut, UserRole
from src.users.service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Annotated[AsyncSession, Depends(get_session)]
) -> UserOut:
    try:
        payload = auth_utils.decode_jwt(token)
        user_id_raw = payload.get(TokenFields.TOKEN_SUB_FIELD.value)
        if user_id_raw is None:
            msg = f"user_id not found in the payload"
            logger.error(msg)
            raise PayloadError(msg)
    except InvalidTokenError:
        logger.error(f"Invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = uuid.UUID(user_id_raw)
    user = await UserService.get_user_by_user_id(
        user_id=user_id,
        session=session
    )
    if user is None:
        msg = f"User not found"
        logger.error(msg)
        raise UserNotFound(msg)

    return UserOut.model_validate(user)


async def get_current_business_user(user: Annotated[UserOut, Depends(get_current_user)]) -> UserOut:
    if user.role == UserRole.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return user
