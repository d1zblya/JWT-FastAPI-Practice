from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import utils as auth_utils
from src.business.dao import BusinessProfileDAO
from src.business.schemas import BusinessProfileInDB
from src.exceptions.exception_business import UserHasNotBusinessProfile
from src.exceptions.exception_user import UserAlreadyExists, UserNotFound, UserCannotUpdate, UserCannotDelete, \
    InvalidPasswordOrUsername, UserCannotAdd
from src.users.dao import UserDAO
from src.users.schemas import UserCreate, UserUpdate, UserInDB
from src.users.utils import try_find_user


class UserService:
    @classmethod
    async def create_user(cls, user: UserCreate, session: AsyncSession) -> UserInDB:
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

            logger.info(f"User successfully created: ID - {new_user.id}")

            return new_user
        except Exception as e:
            await session.rollback()
            msg = f"Error adding user, email - {user.email}"
            logger.error(msg)
            raise UserCannotAdd(msg)

    @classmethod
    async def get_user_by_user_id(cls, user_id: UUID, session: AsyncSession) -> UserInDB:
        existing_user = await try_find_user(session=session, user_id=user_id)
        return existing_user

    @classmethod
    async def get_user_by_email(cls, email: str, session: AsyncSession) -> UserInDB:
        existing_user = await UserDAO.find_one_or_none(session=session, email=email)
        if existing_user is None:
            msg = f"User with email - {email} not found"
            logger.error(msg)
            raise UserNotFound(msg)
        return existing_user

    @classmethod
    async def update_user(cls, user_id: UUID, user: UserUpdate, session: AsyncSession) -> UserInDB:
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

            logger.info(f"User successfully updated: ID - {new_user.id}")

            return new_user
        except Exception as e:
            await session.rollback()
            msg = f"Error updating user (id - {user_id}): {e}"
            logger.error(msg)
            raise UserCannotUpdate(msg)

    @classmethod
    async def delete_user(cls, user_id: UUID, session: AsyncSession) -> None:
        await try_find_user(session=session, user_id=user_id)
        try:
            await UserDAO.delete(session=session, id=user_id)
            await session.commit()

            logger.info(f"User successfully deleted")
        except Exception as e:
            await session.rollback()
            msg = f"Error deleting user (id - {user_id}): {e}"
            logger.error(msg)
            raise UserCannotDelete(msg)

    @classmethod
    async def authenticate_user(cls, email: str, password: str, session: AsyncSession) -> UserInDB:
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

    @classmethod
    async def get_user_business_profile(cls, user_id: UUID, session: AsyncSession) -> BusinessProfileInDB:
        user_business_profile = await BusinessProfileDAO.find_one_or_none(session=session, user_id=user_id)
        if user_business_profile is None:
            msg = f"User with id - {user_id} has not business profile"
            logger.error(msg)
            raise UserHasNotBusinessProfile(msg)

        return user_business_profile
