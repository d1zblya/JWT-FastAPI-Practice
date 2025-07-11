from src.exceptions.dao import CannotUpdateError, CannotDeleteError, NotFoundError, CannotAddError


class CannotAddRefreshToken(CannotAddError):
    pass


class CannotDeleteToken(CannotDeleteError):
    pass


class CannotFindRefreshToken(CannotAddError):
    pass


class CannotDeleteRefreshToken(CannotDeleteError):
    pass
