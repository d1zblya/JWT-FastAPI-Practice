import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenFields(str, Enum):
    TOKEN_TYPE_FIELD = "type"
    TOKEN_SUB_FIELD = "sub"
    TOKEN_EXPIRE_FIELD = "exp"
    TOKEN_IAT_FIELD = "iat"
    TOKEN_JTI_FIELD = "jti"
    TOKEN_ROLE_FIELD = "role"


class TokenTypes(str, Enum):
    ACCESS_TOKEN_TYPE = "access"
    REFRESH_TOKEN_TYPE = "refresh"


class RefreshTokenSchema(BaseModel):
    jti: uuid.UUID = Field(...)
    token: str = Field(...)
    expires_at: datetime = Field(...)
    user_id: uuid.UUID = Field(...)

    model_config = ConfigDict(from_attributes=True)

