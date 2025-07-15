from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, status, Response, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import TokenResponse
from src.auth.service import AuthService
from src.database.session import get_session
from src.users.schemas import UserCreate

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
        user: UserCreate,
        session: Annotated[AsyncSession, Depends(get_session)]
):
    return await AuthService.register(user=user, session=session)


@router.post("/login", response_model=TokenResponse)
async def login_user(
        user: Annotated[OAuth2PasswordRequestForm, Depends()],
        response: Response,
        session: Annotated[AsyncSession, Depends(get_session)]
):
    return await AuthService.login(user=user, response=response, session=session)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
        refresh_token: Annotated[str, Cookie(...)],
        session: Annotated[AsyncSession, Depends(get_session)]
):
    return await AuthService.refresh(refresh_token=refresh_token, session=session)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
        response: Response,
        refresh_token: Annotated[str, Cookie(...)],
        session: Annotated[AsyncSession, Depends(get_session)]
):
    return await AuthService.logout(refresh_token=refresh_token, response=response, session=session)
