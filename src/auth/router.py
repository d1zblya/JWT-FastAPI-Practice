from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, status, Response, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.schemas import TokenResponse
from src.auth.service import AuthService
from src.users.schemas import UserCreate

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    return await AuthService.register(user)


@router.post("/login", response_model=TokenResponse)
async def login_user(
        user: Annotated[OAuth2PasswordRequestForm, Depends()],
        response: Response
):
    return await AuthService.login(user=user, response=response)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(refresh_token: str = Cookie(None)):
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not provided"
        )

    return await AuthService.refresh(refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(response: Response, refresh_token: str = Cookie(None)):
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not provided"
        )

    return await AuthService.logout(refresh_token=refresh_token, response=response)
