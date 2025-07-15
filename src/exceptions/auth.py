from src.exceptions.base import AppError


class AuthError(AppError):
    """Ошибка аутентификации / авторизации"""
    status_code = 401


class LogoutError(AuthError):
    """Общая ошибка при логауте"""
    status_code = 400  # например, неверный запрос на логаут


class TokenCreationError(AuthError):
    """Не удалось создать JWT токен"""
    status_code = 500  # внутренняя ошибка сервера


class TokenVerificationError(AuthError):
    """Не удалось проверить JWT токен"""
    status_code = 401


class TokenExpiredError(TokenVerificationError):
    """Токен просрочен"""
    status_code = 401


class TokenRevokedError(TokenVerificationError):
    """Токен отозван"""
    status_code = 401


class InvalidTokenError(TokenVerificationError):
    """Не соответствие типа токена"""
    status_code = 401


class PayloadError(AuthError):
    """Ошибка обработки payload"""
    status_code = 400
