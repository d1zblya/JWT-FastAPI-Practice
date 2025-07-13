import uuid

from loguru import logger

from src.business.dao import BusinessProfileDAO
from src.business.schemas import UpdateBusinessProfile, CreateBusinessProfile, BusinessProfileOut
from src.business.utils import try_find_business_profile
from src.database.session import async_session_maker
from src.exceptions.business_profile import CannotAddBusinessProfile, CannotUpdateBusinessProfile, \
    CannotDeleteBusinessProfile, UserAlreadyHasBusinessProfile


class BusinessProfileService:
    @classmethod
    async def create_business_profile(cls, business_profile: CreateBusinessProfile) -> BusinessProfileOut:
        async with async_session_maker() as session:
            existing_business_profile = await BusinessProfileDAO.find_one_or_none(
                session=session,
                user_id=business_profile.user_id
            )
            if existing_business_profile:
                msg = f"User with ID: {business_profile.user_id} already has a business profile"
                logger.error(msg)
                raise UserAlreadyHasBusinessProfile(msg)
            try:
                business_profile = await BusinessProfileDAO.add(session=session, obj_in=business_profile)
                session.commit()
                return business_profile
            except Exception as e:
                session.rollback()
                msg = f"Error adding business profile: {e}"
                logger.error(msg)
                raise CannotAddBusinessProfile(msg)

    @classmethod
    async def get_business_profile_by_id(cls, business_id: uuid.UUID) -> BusinessProfileOut:
        async with async_session_maker() as session:
            business_profile = await try_find_business_profile(session=session, business_id=business_id)
            return business_profile

    @classmethod
    async def update_business_profile(cls, business_id: uuid.UUID,
                                      business_profile: UpdateBusinessProfile) -> BusinessProfileOut:
        async with async_session_maker() as session:
            await try_find_business_profile(session=session, business_id=business_id)
            update_data = business_profile.model_dump(exclude_unset=True)

            try:
                new_business_profile = await BusinessProfileDAO.update(
                    session,
                    BusinessProfileDAO.model.id == business_id,
                    obj_in=update_data
                )
                session.commit()
                return new_business_profile
            except Exception as e:
                session.rollback()
                msg = f"Error updating business profile (business_id - {business_id}): {e}"
                logger.error(msg)
                raise CannotUpdateBusinessProfile(msg)

    @classmethod
    async def delete_business_profile(cls, business_id: uuid.UUID) -> None:
        async with async_session_maker() as session:
            await try_find_business_profile(session=session, business_id=business_id)

            try:
                await BusinessProfileDAO.delete(session=session, id=business_id)
                session.commit()
            except Exception as e:
                session.rollback()
                msg = f"Error deleting business profile (business_id - {business_id}): {e}"
                logger.error(msg)
                raise CannotDeleteBusinessProfile(msg)
