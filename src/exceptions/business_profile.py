from src.exceptions.dao import CannotAddError, CannotDeleteError, CannotUpdateError, NotFoundError


class CannotAddBusinessProfile(CannotAddError):
    pass


class BusinessProfileNotFound(NotFoundError):
    pass


class CannotUpdateBusinessProfile(CannotUpdateError):
    pass


class CannotDeleteBusinessProfile(CannotDeleteError):
    pass


class UserAlreadyHasBusinessProfile(CannotAddError):
    pass
