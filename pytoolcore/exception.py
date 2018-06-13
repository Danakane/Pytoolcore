
from pytoolcore import style


class CException(Exception):

    def __str__(self)->str:
        return style.Style.error(super(CException, self).__str__())
