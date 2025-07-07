from src.exceptions.base import AppError


class AuthError(AppError):
    """Ошибка аутентификации / авторизации"""


class TokenCreationError(AuthError):
    """Не удалось создать JWT токен"""


class TokenVerificationError(AuthError):
    """Не удалось проверить JWT токен"""


class AccessTokenExpiredError(TokenVerificationError):
    """Access токен просрочен или отозван"""


class RefreshTokenExpiredError(TokenVerificationError):
    """Refresh токен просрочен или отозван"""
