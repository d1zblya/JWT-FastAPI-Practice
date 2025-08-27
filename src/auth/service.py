import uuid
from datetime import timedelta, datetime, timezone
from typing import Dict, Any

import jwt
from fastapi import HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import utils as auth_utils
from src.auth.dao import RefreshTokenDAO
from src.auth.schemas import TokenFields, TokenTypes, RefreshTokenSchema, TokenResponse, TokensInfo
from src.core.config import settings
from src.database.session import async_session_maker
from src.exceptions.token import CannotAddRefreshToken, CannotFindRefreshToken, CannotDeleteRefreshToken
from src.exceptions.user import UserAlreadyExists, UserNotFound, InvalidPasswordOrUsername
from src.users.schemas import UserJWTRefreshData, UserJWTAccessData, UserCreate, UserRole
from src.users.service import UserService


class TokenService:
    @classmethod
    def create_jwt(
            cls,
            token_type: str,
            token_data: dict,
            expire_minutes: int = settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES,
            expire_timedelta: timedelta = None,
            jti: str | None = None,
    ) -> str:
        """Общая функция создания токена"""
        jwt_payload = {TokenFields.TOKEN_TYPE_FIELD.value: token_type}
        jwt_payload.update(token_data)
        return auth_utils.encode_jwt(
            payload=jwt_payload,
            expire_minutes=expire_minutes,
            expire_timedelta=expire_timedelta,
            jti=jti,
        )

    @classmethod
    async def create_access_token(cls, user: UserJWTAccessData) -> str:
        """Создание access токена"""
        jwt_payload = {
            TokenFields.TOKEN_SUB_FIELD.value: user.id,
            TokenFields.TOKEN_ROLE_FIELD.value: user.role,
        }
        return cls.create_jwt(
            token_type=TokenTypes.ACCESS_TOKEN_TYPE,
            token_data=jwt_payload,
            expire_minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    @classmethod
    async def create_refresh_token(cls, user: UserJWTRefreshData, session: AsyncSession) -> str:
        """Создание refresh токена"""
        jwt_payload = {
            TokenFields.TOKEN_SUB_FIELD.value: user.id,
        }
        jti = uuid.uuid4()

        token = cls.create_jwt(
            token_type=TokenTypes.REFRESH_TOKEN_TYPE,
            token_data=jwt_payload,
            expire_timedelta=timedelta(days=settings.auth.REFRESH_TOKEN_EXPIRE_DAYS),
            jti=str(jti)
        )

        await RefreshTokenService.add_refresh_token(
            RefreshTokenSchema(
                jti=jti,
                token=token,
                expires_at=datetime.now(timezone.utc) + timedelta(days=settings.auth.REFRESH_TOKEN_EXPIRE_DAYS),
                user_id=uuid.UUID(user.id)
            ),
            session=session
        )
        return token

    @classmethod
    async def create_pair_tokens(cls, user_id: str, user_role: UserRole, session: AsyncSession) -> TokensInfo:
        """Создание пары токенов, access и refresh"""
        access_token = await cls.create_access_token(
            UserJWTAccessData(
                id=str(user_id),
                role=user_role,
            )
        )
        refresh_token = await cls.create_refresh_token(
            UserJWTRefreshData(
                id=str(user_id),
            ),
            session=session
        )
        return TokensInfo(access_token=access_token, refresh_token=refresh_token)

    @classmethod
    async def verify_token(
            cls,
            token: str,
            expected_type: TokenTypes = TokenTypes.ACCESS_TOKEN_TYPE
    ) -> Dict[str, Any]:
        """Проверка и декодирование токена"""
        try:
            payload = auth_utils.decode_jwt(token)

            if payload.get(TokenFields.TOKEN_TYPE_FIELD.value) != expected_type.value:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected: {expected_type.value}"
                )

            # Для refresh токена проверяем, что он не отозван
            if expected_type == TokenTypes.REFRESH_TOKEN_TYPE:
                jti = payload.get(TokenFields.TOKEN_JTI_FIELD.value, None)
                async with async_session_maker() as session:
                    token_record = await RefreshTokenDAO.find_one_or_none(session=session, jti=jti)
                    if token_record is None:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Refresh token has been revoked"
                        )
                    if token_record.expires_at < datetime.now(timezone.utc):
                        await RefreshTokenDAO.delete(session=session, jti=jti)
                        await session.commit()
                        raise HTTPException(
                            status.HTTP_401_UNAUTHORIZED,
                            detail="Refresh token expired"
                        )

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )


class AuthService:
    @classmethod
    async def register(cls, user: UserCreate, session: AsyncSession) -> dict | None:
        try:
            new_user = await UserService.create_user(
                user=user,
                session=session
            )
            logger.debug(f"User with ID: {new_user.id} created successfully")
            return {"message": "User created successfully"}
        except UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists"
            )
        except Exception as e:
            logger.error(f"Error with register: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )

    @classmethod
    async def login(
            cls,
            user: OAuth2PasswordRequestForm,
            response: Response,
            session: AsyncSession
    ) -> TokenResponse:
        try:
            user_db = await UserService.authenticate_user(
                email=user.username,  # username = email - особенности FastAPI
                password=user.password,
                session=session
            )
        except UserNotFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        except InvalidPasswordOrUsername:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        tokens_pair = await TokenService.create_pair_tokens(
            user_id=str(user_db.id),
            user_role=user_db.role,
            session=session
        )

        response.set_cookie(
            key="refresh_token",
            value=tokens_pair.refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=settings.auth.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )

        return TokenResponse(access_token=tokens_pair.access_token)

    @classmethod
    async def refresh(cls, refresh_token: str, session: AsyncSession) -> TokenResponse:
        payload = await TokenService.verify_token(
            token=refresh_token,
            expected_type=TokenTypes.REFRESH_TOKEN_TYPE
        )

        user_id = payload.get("sub")

        # берем role из БД тк в payload у refresh токена нету поля role
        user_db = await UserService.get_user_by_user_id(user_id=uuid.UUID(user_id), session=session)

        if user_db is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload"
            )

        user_jwt_data = UserJWTAccessData(id=user_id, role=UserRole(user_db.role))
        access_token = await TokenService.create_access_token(user_jwt_data)

        return TokenResponse(access_token=access_token)

    @classmethod
    async def logout(cls, refresh_token: str, response: Response, session: AsyncSession):
        try:
            payload = await TokenService.verify_token(refresh_token, TokenTypes.REFRESH_TOKEN_TYPE)
            jti = uuid.UUID(payload.get(TokenFields.TOKEN_JTI_FIELD.value))
            token = await RefreshTokenService.get_refresh_token_by_jti(jti=jti, session=session)
            if jti and token:
                await RefreshTokenService.delete_refresh_token(jti=jti, session=session)
        except (ValueError, jwt.PyJWTError) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format"
            )
        except Exception as e:
            logger.error(f"Error with logout: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        response.delete_cookie(
            key="refresh_token",
            httponly=True,
            secure=True,
            samesite="strict"
        )


class RefreshTokenService:
    @staticmethod
    async def get_refresh_token_by_jti(jti: uuid.UUID, session: AsyncSession) -> RefreshTokenSchema:
        token = await RefreshTokenDAO.find_one_or_none(session=session, jti=jti)
        if token is None:
            raise CannotFindRefreshToken(f"Cannot find token")
        logger.debug(f"Token with ID: {jti} found successfully")
        return token

    @staticmethod
    async def add_refresh_token(token_data: RefreshTokenSchema, session: AsyncSession) -> RefreshTokenSchema:
        try:
            new_token = await RefreshTokenDAO.add(session=session, obj_in=token_data)
            await session.commit()
            logger.debug(f"Refresh token with ID: {new_token.jti} created successfully")
            return new_token
        except Exception as e:
            await session.rollback()
            raise CannotAddRefreshToken(f"Cannot add refresh token: {e}")

    @staticmethod
    async def delete_refresh_token(jti: uuid.UUID, session: AsyncSession) -> None:
        try:
            await RefreshTokenDAO.delete(session=session, jti=jti)
            await session.commit()
            logger.debug(f"Refresh token with ID: {jti} deleted successfully")
        except Exception as e:
            await session.rollback()
            raise CannotDeleteRefreshToken(f"Cannot delete refreash token: {e}")
