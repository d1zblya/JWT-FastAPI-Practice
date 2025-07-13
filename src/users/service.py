from uuid import UUID

from loguru import logger

from src.auth import utils as auth_utils
from src.database.session import async_session_maker
from src.exceptions.user import UserAlreadyExists, UserNotFound, UserCannotUpdate, UserCannotDelete, \
    InvalidPasswordOrUsername, UserCannotAdd
from src.users.dao import UserDAO
from src.users.schemas import UserCreate, UserUpdate, UserInDB
from src.users.utils import try_find_user


class UserService:
    @classmethod
    async def create_user(cls, user: UserCreate) -> UserInDB:
        async with async_session_maker() as session:
            existing_user = await UserDAO.find_one_or_none(session=session, email=user.email)
            if existing_user:
                msg = f"User with email {user.email} already exists"
                logger.error(msg)
                raise UserAlreadyExists(msg)

            try:
                user_data = user.model_dump(exclude={"password"})
                hashed_password = auth_utils.hash_password(user.password)
                user_data["hashed_password"] = hashed_password

                new_user = await UserDAO.add(session=session, obj_in=user_data)
                await session.commit()

                return new_user
            except Exception as e:
                session.rollback()
                msg = f"Error adding user, email - {user.email}"
                logger.error(msg)
                raise UserCannotAdd(msg)

    @classmethod
    async def get_user_by_user_id(cls, user_id: UUID) -> UserInDB:
        async with async_session_maker() as session:
            existing_user = await try_find_user(session=session, user_id=user_id)
            return existing_user

    @classmethod
    async def get_user_by_email(cls, email: str) -> UserInDB:
        async with async_session_maker() as session:
            existing_user = await UserDAO.find_one_or_none(session=session, email=email)
            if existing_user is None:
                msg = f"User with email - {email} does not exist"
                logger.error(msg)
                raise UserNotFound(msg)
            return existing_user

    @classmethod
    async def update_user(cls, user_id: UUID, user: UserUpdate) -> UserInDB:
        async with async_session_maker() as session:
            await try_find_user(session=session, user_id=user_id)

            update_data = user.model_dump(exclude_unset=True)

            if "password" in update_data:
                update_data["hashed_password"] = auth_utils.hash_password(update_data.pop("password"))

            try:
                new_user = await UserDAO.update(
                    session,
                    UserDAO.model.id == user_id,
                    obj_in=update_data
                )
                await session.commit()
                return new_user
            except Exception as e:
                msg = f"Error updating user (id - {user_id}): {e}"
                logger.error(msg)
                raise UserCannotUpdate(msg)

    @classmethod
    async def delete_user(cls, user_id: UUID) -> None:
        async with async_session_maker() as session:
            await try_find_user(session=session, user_id=user_id)
            try:
                await UserDAO.delete(session=session, id=user_id)
                await session.commit()
            except Exception as e:
                msg = f"Error deleting user (id - {user_id}): {e}"
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
