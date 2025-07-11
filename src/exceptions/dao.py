from src.exceptions.base import AppError


class DAOError(AppError):
    """Общая ошибка слоя доступа к данным"""


class CannotAddError(DAOError):
    """Ошибка добавления записи в БД"""


class CannotUpdateError(DAOError):
    """Ошибка обновления записи в БД"""


class CannotDeleteError(DAOError):
    """Ошибка удаления записи из БД"""


class NotFoundError(DAOError):
    """Запись не найдена в БД"""


class AlreadyExistsError(DAOError):
    """Запись уже существует"""


class InvalidCredentialsError(DAOError):
    """Неверные данные"""
