from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.business.schemas import BusinessProfileOut
from src.database.session import get_session
from src.users.dependencies import get_current_user
from src.users.schemas import UserOut, UserUpdate
from src.users.service import UserService

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
)


@router.get("/me", response_model=UserOut)
async def read_user(
        user: Annotated[UserOut, Depends(get_current_user)]
) -> UserOut:
    return user


@router.put("/me", response_model=UserOut, response_model_exclude_unset=True)
async def update_user(
        new_user: UserUpdate,
        user: Annotated[UserOut, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_session)]
):
    return await UserService.update_user(
        user_id=user.id,
        user=new_user,
        session=session
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user: Annotated[UserOut, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_session)]
):
    await UserService.delete_user(user_id=user.id, session=session)


@router.get("/business-profile", response_model=BusinessProfileOut)
async def get_user_business_profile(
        user: Annotated[UserOut, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_session)]
):
    return await UserService.get_user_business_profile(user_id=user.id, session=session)
