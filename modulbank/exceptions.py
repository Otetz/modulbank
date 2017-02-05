class ModulbankException(Exception):
    pass


class NotAuthorizedModulbankException(ModulbankException):
    pass


class UnexpectedResponseStatusModulbankException(ModulbankException):
    pass


class UnexpectedResponseBodyModulbankException(ModulbankException):
    pass


class UnexpectedValueModulbankException(ModulbankException):
    pass
