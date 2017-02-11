class ModulbankException(Exception):
    """
    Базовый класс для исключений пакета.
    """
    pass


class NotAuthorizedModulbankException(ModulbankException):
    """
    Возникает если не прошли авторизацию.
    """
    pass


class UnexpectedResponseStatusModulbankException(ModulbankException):
    """
    Возникает если статус ответа сервера отлиается от ожидаемого.
    """
    pass


class UnexpectedResponseBodyModulbankException(ModulbankException):
    """
    Возникает если не удалось обработать полученные данные.
    """
    pass


class UnexpectedValueModulbankException(ModulbankException):
    """
    Возникает если не удалось конвертировать полученное значение.
    """
    pass
