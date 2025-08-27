from src.exceptions.exception_dao import AlreadyExistsError, NotFoundError, CannotUpdateError, CannotDeleteError, \
    InvalidCredentialsError, CannotAddError


class UserAlreadyExists(AlreadyExistsError):
    pass


class UserCannotAdd(CannotAddError):
    pass


class UserNotFound(NotFoundError):
    pass


class UserCannotUpdate(CannotUpdateError):
    pass


class UserCannotDelete(CannotDeleteError):
    pass


class InvalidPasswordOrUsername(InvalidCredentialsError):
    pass
