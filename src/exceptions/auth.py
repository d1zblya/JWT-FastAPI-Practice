from src.exceptions.base import AppError


class AuthError(AppError):
    """Ошибка аутентификации / авторизации"""


class LogoutError(AuthError):
    """Общая ошибка при логауте"""


class TokenCreationError(AuthError):
    """Не удалось создать JWT токен"""


class TokenVerificationError(AuthError):
    """Не удалось проверить JWT токен"""


class TokenExpiredError(TokenVerificationError):
    """Токен просрочен"""


class TokenRevokedError(TokenVerificationError):
    """Токен отозван"""


class InvalidTokenError(TokenVerificationError):
    """Не соответствие типа токена"""


class PayloadError(AuthError):
    """Ошибка обработки payload"""
