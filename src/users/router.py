from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.testing.pickleable import User

from src.users.dependencies import get_current_user
from src.users.schemas import UserOut

router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)


@router.get("/me", response_model=UserOut)
async def read_user(
    current_user: Annotated[UserOut, Depends(get_current_user)]
) -> UserOut:
    return current_user
