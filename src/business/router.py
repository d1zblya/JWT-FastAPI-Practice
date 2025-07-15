import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.business.schemas import BusinessProfileOut, BusinessProfileCreate, BusinessProfileUpdate
from src.business.service import BusinessProfileService
from src.database.session import get_session
from src.users.dependencies import get_current_business_user
from src.users.schemas import UserOut

router = APIRouter(
    prefix="/api/business-profile",
    tags=["business"],
)


@router.get("/{business_id}", response_model=BusinessProfileOut)
async def get_business(
        business_id: uuid.UUID,
        business_user: Annotated[UserOut, Depends(get_current_business_user)],
        session: Annotated[AsyncSession, Depends(get_session)]
):
    return await BusinessProfileService.get_business_profile_by_id(
        business_id=business_id,
        user_id=business_user.id,
        session=session
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=BusinessProfileOut)
async def create_business(
        business_profile: BusinessProfileCreate,
        business_user: Annotated[UserOut, Depends(get_current_business_user)],
        session: Annotated[AsyncSession, Depends(get_session)]
):
    business_profile.user_id = business_user.id
    return await BusinessProfileService.create_business_profile(
        business_profile=business_profile,
        session=session
    )


@router.put("/{business_id}", response_model=BusinessProfileOut)
async def update_business(
        business_id: uuid.UUID,
        business_profile: BusinessProfileUpdate,
        business_user: Annotated[UserOut, Depends(get_current_business_user)],
        session: Annotated[AsyncSession, Depends(get_session)]
):
    return await BusinessProfileService.update_business_profile(
        business_id=business_id,
        business_profile=business_profile,
        user_id=business_user.id,
        session=session
    )


@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business(
        business_id: uuid.UUID,
        business_user: Annotated[UserOut, Depends(get_current_business_user)],
        session: Annotated[AsyncSession, Depends(get_session)]
):
    await BusinessProfileService.delete_business_profile(
        business_id=business_id,
        user_id=business_user.id,
        session=session
    )
