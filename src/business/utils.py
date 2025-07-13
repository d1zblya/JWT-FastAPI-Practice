import uuid

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.business.dao import BusinessProfileDAO
from src.business.schemas import BusinessProfileOut
from src.exceptions.business_profile import BusinessProfileNotFound


async def try_find_business_profile(session: AsyncSession, business_id: uuid.UUID) -> BusinessProfileOut:
    existing_business_profile = await BusinessProfileDAO.find_one_or_none(
        session=session,
        id=business_id
    )
    if existing_business_profile is None:
        msg = f"Business profile with ID: {business_id} not found"
        logger.error(msg)
        raise BusinessProfileNotFound(msg)
    return existing_business_profile
