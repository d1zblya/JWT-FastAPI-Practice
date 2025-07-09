import uuid
from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, status, Response, Depends
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger

from src.auth.schemas import TokenResponse, TokenTypes
from src.auth.service import AuthService, RefreshTokenService
from src.core.config import settings
from src.exceptions.auth import LogoutError
from src.users.schemas import UserCreate, UserJWTData
from src.users.service import UserService

router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"],
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    try:
        await UserService.create_user(user)
        return {"message": "User created successfully"}
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed"
        )


@router.post("/login")
async def login_user(
        user: Annotated[OAuth2PasswordRequestForm, Depends()],
        response: Response
) -> TokenResponse:
    user_db = await UserService.authenticate_user(email=user.username, password=user.password)  # username = email

    if user_db is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_jwt_data = UserJWTData(
        id=str(user_db.id),
        role=user_db.role,
    )

    access_token = await AuthService.create_access_token(user_jwt_data)
    refresh_token = await AuthService.create_refresh_token(user_jwt_data)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.auth.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

    return TokenResponse(access_token=access_token)


@router.post("/refresh")
async def refresh_access_token(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not provided"
        )
    try:
        payload = await AuthService.verify_token(
            token=refresh_token,
            expected_type=TokenTypes.REFRESH_TOKEN_TYPE.value
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    user_role = payload.get("role")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload"
        )

    user_jwt_data = UserJWTData(id=user_id, role=user_role)
    access_token = await AuthService.create_access_token(user_jwt_data)

    return TokenResponse(access_token=access_token)


@router.post("/logout")
async def logout_user(response: Response, refresh_token: str = Cookie(None)):
    if refresh_token:
        try:
            payload = await AuthService.verify_token(refresh_token, TokenTypes.REFRESH_TOKEN_TYPE.value)
            jti = uuid.UUID(payload.get("jti"))
            token = await RefreshTokenService.get_refresh_token_by_jti(jti)
            if jti and token:
                await RefreshTokenService.delete_refresh_token(jti)
        except Exception as e:
            raise LogoutError(f"Logout error: {e}")

    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="strict"
    )
    return {"message": "Logged out successfully"}
