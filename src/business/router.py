import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from src.business.schemas import CreateBusinessProfile, UpdateBusinessProfile
from src.business.service import BusinessProfileService
from src.users.dependencies import get_current_user

router = APIRouter(
    prefix="/api/business-profile",
    tags=["business"],
)


@router.get("/{business_id}")
async def get_business(
        business_id: uuid.UUID,
        user: Annotated[get_current_user, Depends()]
):
    return await BusinessProfileService.get_business_profile_by_id(business_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_business(
        business_profile: CreateBusinessProfile,
        user: Annotated[get_current_user, Depends()]
):
    return await BusinessProfileService.create_business_profile(business_profile)


@router.put("/{business_id}")
async def update_business(
        business_id: uuid.UUID,
        business_profile: UpdateBusinessProfile,
        user: Annotated[get_current_user, Depends()]
):
    return await BusinessProfileService.update_business_profile(
        business_id=business_id,
        business_profile=business_profile
    )


@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business(
        business_id: uuid.UUID,
        user: Annotated[get_current_user, Depends()]
):
    await BusinessProfileService.delete_business_profile(business_id)
