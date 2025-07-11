import re
import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator


###############
# User Schemas #
###############

class UserRole(str, Enum):
    BUSINESS = "business"
    USER = "user"


# Общая база (без id, пароля и дат)
class UserBase(BaseModel):
    """Базовая модель, от которой наследуются другие (Create, Out, InDB и т.д.)"""
    email: EmailStr = Field(..., description="Электронная почта", max_length=100, example="user@example.com")
    first_name: str | None = Field(default=None, description="Имя пользователя", max_length=50)
    last_name: str | None = Field(default=None, description="Фамилия пользователя", max_length=50)
    phone: str | None = Field(default=None, description="Номер телефона", max_length=20)
    role: UserRole = Field(default=UserRole.USER.value, description="Роль пользователя")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is not None:
            # Простая валидация для международного формата
            if not re.match(r'^\+?[1-9]\d{1,14}$', v):
                raise ValueError('Некорректный формат телефона')
        return v

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_names(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
            if not re.match(r'^[a-zA-Zа-яА-Я\s\-\']+$', v):
                raise ValueError('Имя может содержать только буквы, пробелы, дефисы и апострофы')
        return v


# Модель для создания (регистрация)
class UserCreate(UserBase):
    """Используется в POST-запросах для создания пользователя"""
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        # pattern=r"^[a-zA-Zа-яА-Я\s\-\']+$",
        description="Пароль (минимум 8 символов)"
    )

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d).+$", v):
            raise ValueError("Пароль должен содержать как минимум одну букву и одну цифру (не менее 8 символов)")
        return v


# Модель для обновления (все поля опциональны)
class UserUpdate(BaseModel):
    """Используется в PATCH/PUT-запросах для обновления информации о пользователе"""
    email: EmailStr | None = Field(default=None, description="Новый email", example="user@example.com")
    first_name: str | None = Field(default=None, description="Имя", max_length=50)
    last_name: str | None = Field(default=None, description="Фамилия", max_length=50)
    phone: str | None = Field(default=None, description="Телефон", max_length=20)
    role: UserRole | None = Field(default=None, description="Роль")
    password: str | None = Field(
        None,
        min_length=8,
        # pattern=r"^[a-zA-Zа-яА-Я\s\-\']+$",
        description="Новый пароль"
    )

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d).+$", v):
            raise ValueError("Пароль должен содержать как минимум одну букву и одну цифру (не менее 8 символов)")
        return v


# Модкль для логина пользователя
class UserLogin(BaseModel):
    """Схема для логина (аутентификации)"""
    email: EmailStr = Field(..., description="Электронная почта", example="user@example.com")
    password: str = Field(..., description="Пароль")


# Модель вывода (ответ клиенту)
class UserOut(UserBase):
    """Модель для ответа клиенту (response_model)"""
    id: uuid.UUID = Field(..., description="ID пользователя")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата последнего обновления")

    model_config = ConfigDict(from_attributes=True)


# Модель для работы с JWT access
class UserJWTAccessData(BaseModel):
    """Модель для работы с JWT (создание access токена)"""
    id: str
    role: UserRole


# Модель для работы с JWT refresh
class UserJWTRefreshData(BaseModel):
    """Модель для работы с JWT (создание refresh токена)"""
    id: str


# Внутренняя модель (включает хэш пароля)
class UserInDB(UserOut):
    """Внутренняя модель, используемая внутри сервиса/репозитория/ORM, но не отдаётся клиенту"""
    hashed_password: str = Field(..., description="Хэш пароля")

    model_config = ConfigDict(from_attributes=True)

    def to_public(self) -> UserOut:
        return UserOut.model_validate(self)

####################
# Business Schemas #
####################
