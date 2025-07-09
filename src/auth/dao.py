from src.auth.models import RefreshTokenModel
from src.database.base import BaseDAO


class RefreshTokenDAO(BaseDAO):
    model = RefreshTokenModel
