
from pytoolcore import style


class ErrorException(Exception):

    def __str__(self)->str:
        return style.Style.error(super(ErrorException, self).__str__())


class FailureException(Exception):

    def __str__(self)->str:
        return style.Style.failure(super(FailureException, self).__str__())


class WarningException(Exception):

    def __str__(self)->str:
        return style.Style.warning(super(WarningException, self).__str__())


class InfoException(Exception):

    def __str__(self)->str:
        return style.Style.info(super(InfoException, self).__str__())


class SuccessException(Exception):

    def __str__(self)->str:
        return style.Style.success(super(SuccessException, self).__str__())
