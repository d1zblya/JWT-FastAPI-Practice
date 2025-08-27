from src.exceptions.exception_dao import CannotAddError, CannotDeleteError, CannotUpdateError, NotFoundError, AlreadyExistsError


class CannotAddBusinessProfile(CannotAddError):
    pass


class BusinessProfileNotFound(NotFoundError):
    pass


class CannotUpdateBusinessProfile(CannotUpdateError):
    pass


class CannotDeleteBusinessProfile(CannotDeleteError):
    pass


class UserAlreadyHasBusinessProfile(AlreadyExistsError):
    pass


class UserHasNotBusinessProfile(NotFoundError):
    pass
