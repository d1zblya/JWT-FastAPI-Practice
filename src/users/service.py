from uuid import UUID

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from src.auth import utils as auth_utils
from src.database.session import async_session_maker
from src.exceptions.dao import CannotAddError
from src.exceptions.user import UserAlreadyExists, UserNotFound, UserCannotUpdate, UserCannotDelete, \
    InvalidPasswordOrUsername
from src.users.dao import UserDAO
from src.users.schemas import UserCreate, UserUpdate, UserInDB, UserLogin


class UserService:
    @classmethod
    async def create_user(cls, user: UserCreate) -> UserInDB:
        async with async_session_maker() as session:
            existing_user = await UserDAO.find_one_or_none(session=session, email=user.email)
            if existing_user:
                msg = f"User with email {user.email} already exists"
                logger.error(msg)
                raise UserAlreadyExists(msg)

            user_data = user.model_dump(exclude={"password"})
            hashed_password = auth_utils.hash_password(user.password)
            user_data["hashed_password"] = hashed_password

            new_user = await UserDAO.add(session=session, obj_in=user_data)
            await session.commit()

            return new_user

    @classmethod
    async def get_user(cls, user_id: UUID) -> UserInDB:
        async with async_session_maker() as session:
            user = await UserDAO.find_one_or_none(session=session, id=user_id)
            if user is None:
                msg = f"User with id - {user_id} does not exist"
                logger.error(msg)
                raise UserNotFound(msg)
            return user

    @classmethod
    async def get_user_by_email(cls, email: str) -> UserInDB:
        async with async_session_maker() as session:
            user = await UserDAO.find_one_or_none(session=session, email=email)
            if user is None:
                msg = f"User with email - {email} does not exist"
                logger.error(msg)
                raise UserNotFound(msg)
            return user

    @classmethod
    async def update_user(cls, user_id: UUID, user: UserUpdate) -> UserInDB:
        async with async_session_maker() as session:
            existing_user = await UserDAO.find_one_or_none(session=session, id=user_id)
            if existing_user is None:
                msg = f"User with id - {user_id} does not exist"
                logger.error(msg)
                raise UserNotFound(msg)

            update_data = user.model_dump(exclude_unset=True)

            if "password" in update_data:
                update_data["hashed_password"] = auth_utils.hash_password(update_data.pop("password"))

            try:
                new_user = await UserDAO.update(
                    session=session,
                    *[UserDAO.model.id == user_id],
                    obj_in=update_data
                )
                await session.commit()
                return new_user
            except Exception as e:
                msg = f"Error with update user (id - {user_id}): {e}"
                logger.error(msg)
                raise UserCannotUpdate(msg)

    @classmethod
    async def delete_user(cls, user_id: UUID) -> None:
        async with async_session_maker() as session:
            user = await UserDAO.find_one_or_none(session=session, id=user_id)
            if user is None:
                raise UserNotFound(f"User with id - {user_id} does not exist")
            try:
                await UserDAO.delete(session=session, id=user_id)
                await session.commit()
            except Exception as e:
                msg = f"Error with delete user (id - {user_id}): {e}"
                logger.error(msg)
                raise UserCannotDelete(msg)

    @classmethod
    async def authenticate_user(cls, email: str, password: str) -> UserInDB:
        async with async_session_maker() as session:
            user = await UserDAO.find_one_or_none(session=session, email=email)

            if user is None:
                msg = f"User with email - {email} does not exist"
                logger.error(msg)
                raise UserNotFound(msg)

            if not auth_utils.verify_password(password, user.hashed_password):
                msg = f"Incorrect username or password"
                logger.error(msg)
                raise InvalidPasswordOrUsername(msg)

            return user
