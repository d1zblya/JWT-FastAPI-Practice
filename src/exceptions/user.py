from src.exceptions.dao import AlreadyExistsError, NotFoundError


class UserAlreadyExists(AlreadyExistsError):
    pass


class UserNotFound(NotFoundError):
    pass
