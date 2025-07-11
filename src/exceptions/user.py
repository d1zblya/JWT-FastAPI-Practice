from src.exceptions.dao import AlreadyExistsError, NotFoundError, CannotUpdateError, CannotDeleteError, \
    InvalidCredentialsError


class UserAlreadyExists(AlreadyExistsError):
    pass


class UserNotFound(NotFoundError):
    pass


class UserCannotUpdate(CannotUpdateError):
    pass


class UserCannotDelete(CannotDeleteError):
    pass


class InvalidPasswordOrUsername(InvalidCredentialsError):
    pass
