from src.exceptions.exception_dao import CannotDeleteError, NotFoundError, CannotAddError


class CannotAddRefreshToken(CannotAddError):
    pass


class CannotDeleteToken(CannotDeleteError):
    pass


class CannotFindRefreshToken(NotFoundError):
    pass


class CannotDeleteRefreshToken(CannotDeleteError):
    pass
