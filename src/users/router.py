from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from src.users.dependencies import get_current_user
from src.users.schemas import UserOut, UserUpdate
from src.users.service import UserService

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
)


@router.get("/me", response_model=UserOut)
async def read_user(
        current_user: Annotated[UserOut, Depends(get_current_user)]
) -> UserOut:
    return current_user


@router.put("/me", response_model=UserOut, response_model_exclude_unset=True)
async def update_user(
        new_user: UserUpdate,
        current_user: Annotated[UserOut, Depends(get_current_user)]
):
    return await UserService.update_user(
        user_id=current_user.id,
        user=new_user,
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        current_user: Annotated[UserOut, Depends(get_current_user)]
):
    await UserService.delete_user(current_user.id)
