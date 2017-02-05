import logging

from .client import ModulbankClient, SearchOptions
from .client_bank_exchange import ClientBankExchange
from .exceptions import *
from .structs import *

try:
    logging.getLogger(__name__).addHandler(logging.NullHandler())
# pragma: no cover
except AttributeError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


    logging.getLogger(__name__).addHandler(NullHandler())
