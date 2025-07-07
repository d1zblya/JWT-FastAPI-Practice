from uuid import UUID

from loguru import logger

from src.database.session import async_session_maker
from src.users.dao import UserDAO
from src.users.schemas import UserCreate, UserUpdate


class UserService:
    @classmethod
    async def create_user(cls, user: UserCreate):
        pass

    @classmethod
    async def get_user(cls, user_id: UUID):
        pass

    @classmethod
    async def update_user(cls, user_id: UUID, user: UserUpdate):
        pass
