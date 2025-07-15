import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class WorkingHour(BaseModel):
    day: str = Field(..., description="День недели")
    from_time: str = Field(..., description="Время начала работы (чч:мм)")
    to_time: str = Field(..., description="Время окончания работы (чч:мм)")


class BusinessProfileBase(BaseModel):
    business_name: str | None = Field(default=None, description="Название бизнеса")
    description: str | None = Field(default=None, description="Описание бизнеса")
    address: str | None = Field(default=None, description="Адрес")
    working_hours: list[WorkingHour] | None = Field(default=None, description="Рабочие часы")


class BusinessProfileCreate(BusinessProfileBase):
    user_id: uuid.UUID = Field(..., description="ID пользователя (владельца профиля)")


class BusinessProfileUpdate(BusinessProfileBase):
    business_name: str | None = Field(default=None, description="Новое название бизнеса")
    description: str | None = Field(default=None, description="Новое описание")
    address: str | None = Field(default=None, description="Новый адрес")
    working_hours: list[WorkingHour] | None = Field(default=None, description="Новые рабочие часы")


class BusinessProfileOut(BusinessProfileBase):
    id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class BusinessProfileInDB(BusinessProfileOut):
    """Модель для работы внутри сервиса или репозитория"""
    pass
