from src.business.models import BusinessProfileModel
from src.database.base import BaseDAO


class BusinessProfileDAO(BaseDAO):
    model = BusinessProfileModel
