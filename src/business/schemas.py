import uuid
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class WorkingHour(BaseModel):
    day: str
    from_time: str
    to_time: str


class BusinessProfileBase(BaseModel):
    """Базовая модель для бизнес профиля"""
    business_name: str | None = Field(default=None, description="Название бизнеса")
    description: str | None = Field(default=None, description="Описание бизнеса")
    address: str | None = Field(default=None, description="Адрес")
    working_hours: list[WorkingHour] | None = Field(default=None, description="Рабочие часы")


class CreateBusinessProfile(BusinessProfileBase):
    """Модель для создания бизнес профиля"""
    user_id: uuid.UUID = Field(..., description="ID пользователя")


class UpdateBusinessProfile(BusinessProfileBase):
    """Модель для обновления бизнес профиля"""


class BusinessProfileOut(BusinessProfileBase):
    """Модель для ответа пользователю"""
    id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(..., description="ID пользователя")

    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата последнего обновления")

    model_config = ConfigDict(from_attributes=True)
