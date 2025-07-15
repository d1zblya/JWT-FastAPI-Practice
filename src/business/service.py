import uuid

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.business.dao import BusinessProfileDAO
from src.business.schemas import BusinessProfileInDB, BusinessProfileUpdate, BusinessProfileCreate
from src.business.utils import try_find_business_profile
from src.database.session import async_session_maker
from src.exceptions.auth import NotEnoughPermissions
from src.exceptions.business_profile import CannotAddBusinessProfile, CannotUpdateBusinessProfile, \
    CannotDeleteBusinessProfile, UserAlreadyHasBusinessProfile


class BusinessProfileService:
    @classmethod
    async def create_business_profile(
            cls,
            business_profile: BusinessProfileCreate,
            session: AsyncSession
    ) -> BusinessProfileInDB:
        existing_business_profile = await BusinessProfileDAO.find_one_or_none(
            session=session,
            user_id=business_profile.user_id
        )
        if existing_business_profile:
            msg = f"User with ID: {business_profile.user_id} already has a business profile"
            logger.error(msg)
            raise UserAlreadyHasBusinessProfile(msg)
        try:
            business_profile_db = await BusinessProfileDAO.add(session=session, obj_in=business_profile)
            await session.commit()
            logger.debug(f"Created business profile: {business_profile_db.id}")
            return business_profile_db
        except Exception as e:
            await session.rollback()
            msg = f"Error adding business profile: {e}"
            logger.error(msg)
            raise CannotAddBusinessProfile(msg)

    @classmethod
    async def get_business_profile_by_id(
            cls,
            business_id: uuid.UUID,
            user_id: uuid.UUID,
            session: AsyncSession
    ) -> BusinessProfileInDB:
        business_profile = await try_find_business_profile(session=session, business_id=business_id)

        if business_profile.user_id != user_id:
            raise NotEnoughPermissions("Not enough permissions to get this business profile")

        return business_profile

    @classmethod
    async def update_business_profile(
            cls,
            business_id: uuid.UUID,
            business_profile: BusinessProfileUpdate,
            user_id: uuid.UUID,
            session: AsyncSession
    ) -> BusinessProfileInDB:
        existing_profile = await try_find_business_profile(session=session, business_id=business_id)

        if existing_profile.user_id != user_id:
            raise NotEnoughPermissions("Not enough permissions to update this business profile")

        update_data = business_profile.model_dump(exclude_unset=True)
        try:
            new_business_profile = await BusinessProfileDAO.update(
                session,
                BusinessProfileDAO.model.id == business_id,
                obj_in=update_data
            )
            await session.commit()
            logger.debug(f"Updated business profile: {new_business_profile.id}")
            return new_business_profile
        except Exception as e:
            await session.rollback()
            msg = f"Error updating business profile (business_id - {business_id}): {e}"
            logger.error(msg)
            raise CannotUpdateBusinessProfile(msg)

    @classmethod
    async def delete_business_profile(
            cls,
            business_id: uuid.UUID,
            user_id: uuid.UUID,
            session: AsyncSession
    ) -> None:
        existing_profile = await try_find_business_profile(session=session, business_id=business_id)

        if existing_profile.user_id != user_id:
            raise NotEnoughPermissions("Not enough permissions to delete this business profile")

        try:
            await BusinessProfileDAO.delete(session=session, id=business_id)
            logger.debug(f"Deleted business profile: {business_id}")
            await session.commit()
        except Exception as e:
            await session.rollback()
            msg = f"Error deleting business profile (business_id - {business_id}): {e}"
            logger.error(msg)
            raise CannotDeleteBusinessProfile(msg)
