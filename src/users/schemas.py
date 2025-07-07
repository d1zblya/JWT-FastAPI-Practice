import uuid
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, ConfigDict


###############
# User Models #
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
    role: UserRole = Field(..., description="Роль пользователя")


# Модель для создания (регистрация)
class UserCreate(UserBase):
    """Используется в POST-запросах для создания пользователя"""
    password: str = Field(
        ...,
        min_length=8,
        regex=r"^(?=.*[A-Za-z])(?=.*\d).+$",
        description="Пароль (минимум 8 символов)"
    )


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
        regex=r"^(?=.*[A-Za-z])(?=.*\d).+$",
        description="Новый пароль"
    )


# Модель вывода (ответ клиенту)
class UserOut(UserBase):
    """Модель для ответа клиенту (response_model)"""
    id: uuid.UUID = Field(..., description="ID пользователя")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата последнего обновления")

    model_config = ConfigDict(from_attributes=True)


# Внутренняя модель (включает хэш пароля)
class UserInDB(UserOut):
    """Внутренняя модель, используемая внутри сервиса/репозитория/ORM, но не отдаётся клиенту"""
    hashed_password: str = Field(..., description="Хэш пароля")

    model_config = ConfigDict(from_attributes=True)


###################
# Business Models #
###################


