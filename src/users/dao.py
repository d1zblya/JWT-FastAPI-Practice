from src.database.base import BaseDAO
from src.users.models import UserModel


class UserDAO(BaseDAO):
    model = UserModel
