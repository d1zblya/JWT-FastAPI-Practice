from src.exceptions.base import AppError


class DAOError(AppError):
    """Общая ошибка слоя доступа к данным"""
    status_code = 500  # базовый для DAO-проблем


class CannotAddError(DAOError):
    """Ошибка добавления записи в БД"""
    status_code = 500


class CannotUpdateError(DAOError):
    """Ошибка обновления записи в БД"""
    status_code = 500


class CannotDeleteError(DAOError):
    """Ошибка удаления записи из БД"""
    status_code = 500


class NotFoundError(DAOError):
    """Запись не найдена в БД"""
    status_code = 404


class AlreadyExistsError(DAOError):
    """Запись уже существует"""
    status_code = 409


class InvalidCredentialsError(DAOError):
    """Неверные данные"""
    status_code = 401
