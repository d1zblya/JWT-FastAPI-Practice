import uuid
from loguru import logger

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.user import UserNotFound
from src.users.dao import UserDAO
from src.users.schemas import UserInDB


async def try_find_user(session: AsyncSession, user_id: uuid.UUID) -> UserInDB:
    existing_user = await UserDAO.find_one_or_none(session=session, id=user_id)
    if existing_user is None:
        msg = f"User with id - {user_id} does not exist"
        logger.error(msg)
        raise UserNotFound(msg)
    return existing_user
