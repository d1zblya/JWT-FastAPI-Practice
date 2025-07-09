import uuid
from datetime import timedelta, datetime, timezone
from typing import Dict, Any

import jwt
from fastapi import HTTPException, status

from src.auth import utils as auth_utils
from src.auth.dao import RefreshTokenDAO
from src.auth.schemas import TokenFields, TokenTypes, RefreshTokenSchema
from src.core.config import settings
from src.database.session import async_session_maker
from src.exceptions.token import CannotFindToken, CannotAddRefreshToken
from src.users.schemas import UserJWTData


class AuthService:
    @classmethod
    def create_jwt(
            cls,
            token_type: str,
            token_data: dict,
            expire_minutes: int = settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES,
            expire_timedelta: timedelta = None,
            jti: str | None = None,
    ) -> str:
        jwt_payload = {TokenFields.TOKEN_TYPE_FIELD.value: token_type}
        jwt_payload.update(token_data)
        return auth_utils.encode_jwt(
            payload=jwt_payload,
            expire_minutes=expire_minutes,
            expire_timedelta=expire_timedelta,
            jti=jti,
        )

    @classmethod
    async def create_access_token(cls, user: UserJWTData) -> str:
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
    async def create_refresh_token(cls, user: UserJWTData) -> str:
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
                user_id=user.id
            )
        )
        return token

    @classmethod
    async def verify_token(cls, token: str,
                           expected_type: TokenTypes = TokenTypes.ACCESS_TOKEN_TYPE) -> Dict[str, Any]:
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
                jti = payload.get(TokenFields.TOKEN_JTI_FIELD.value)
                async with async_session_maker() as session:
                    token_record = await RefreshTokenDAO.find_one_or_none(session=session, jti=jti)
                    if not jti or token_record is None:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Refresh token has been revoked"
                        )
                    if token_record.expires_at < datetime.utcnow():
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


class RefreshTokenService:
    @staticmethod
    async def get_refresh_token_by_jti(jti: uuid.UUID) -> RefreshTokenSchema:
        async with async_session_maker() as session:
            try:
                token = await RefreshTokenDAO.find_one_or_none(session=session, jti=jti)
                if token is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="JWT token not found"
                    )
                return token
            except Exception as e:
                raise CannotFindToken(f"Cannot find token: {e}")

    @staticmethod
    async def add_refresh_token(token_data: RefreshTokenSchema) -> RefreshTokenSchema:
        async with async_session_maker() as session:
            try:
                new_token = await RefreshTokenDAO.add(session=session, obj_in=token_data)
                await session.commit()
                return new_token
            except Exception as e:
                raise CannotAddRefreshToken(f"Cannot add refresh token: {e}")

    @staticmethod
    async def delete_refresh_token(jti: uuid.UUID) -> None:
        async with async_session_maker() as session:
            try:
                await RefreshTokenDAO.delete(session=session, jti=jti)
                await session.commit()
            except Exception as e:
                pass
