class AppError(Exception):
    """Базовый класс для всех ошибок приложения"""
    status_code: int = 400

    def __init__(self, message: str = None):
        self.message = message or self.__class__.__name__
        super().__init__(self.message)
