import datetime
from decimal import Decimal, InvalidOperation

import requests

from .client_bank_exchange import ClientBankExchange
from .exceptions import *
from .structs import Company, Operation, OperationCategory, PaymentOrder


class SearchOptions:
    """
    Критерии отбора операций при поиске.
    """

    def __init__(self, category: OperationCategory = None, date_from: datetime.date = None,
                 date_till: datetime.date = None,
                 page: int = 0):
        """
        Конструктор

        :param category: Направление платежа. Возможные значения см. в `SearchCategory`
        :param date_from: Вывести операции от момента времени (дата проведения которых равна указанной, или младше)
        :param date_till: Вывести операции до момента времени (дата проведения которых равна указанной, или старше)
        :param page: Номер страницы постраничного вывода (начиная с 0, размер определяется в :class:`ModulbankClient`)
        """
        self.__category = category
        self.__from = date_from
        self.__till = date_till
        self.__page = page

    @property
    def category(self) -> OperationCategory:
        """
        Направление платежа

        Возможные значения:
         - `OperationCategory.Debet` - входящий;
         - `OperationCategory.Credit` - исходящий
        :return: `OperationCategory`
        """
        return self.__category

    @property
    def date_from(self) -> datetime.date:
        """
        Вывести операции от момента времени

        :return: Момент времен "от" `datetime.date`
        """
        return self.__from

    @property
    def date_till(self) -> datetime.date:
        """
        Вывести операции до момента времени

        :return: Момент времен "до" `datetime.date`
        """
        return self.__till

    @property
    def page(self) -> int:
        """
        Номер страницы постраничного вывода

        Начиная с 0, размер определяется в конструкторе :class:`ModulbankClient`

        :return: Номер страницы
        """
        return self.__page

    def to_dict(self) -> {}:
        """
        Возвращает парметры поиска в виде словаря (для последующей запаковки в JSOn-объект).

        :return: Словарь критериев поиска.
        """
        criteria = {}
        if self.category:
            criteria['category'] = str(self.category).replace('OperationCategory.', '')
        if self.date_from:
            criteria['from'] = self.date_from.strftime('%Y-%m-%d')
        if self.date_till:
            criteria['till'] = self.date_till.strftime('%Y-%m-%d')
        if self.page is not None:
            criteria['page'] = self.page
        return criteria


class PaymentResponse:
    """
    Ответ на импорт платежек в API МодульБанка
    """

    def __init__(self, obj: {}):
        """
        Конструктор

        :param obj: JSON-объект ответа на импорт платежек в API МодульБанка.
        """
        if 'totalLoaded' in obj:
            self.__total_loaded = obj['totalLoaded']
        if 'errors' in obj:
            self.__errors = obj['errors']
        else:
            self.__errors = []

    @property
    def total_loaded(self) -> int:
        """
        Количество загруженных платежных поручений

        :return: Количество загруженных платежных поручений
        """
        return self.__total_loaded

    @property
    def errors(self) -> []:
        """
        Ошибки по незагруженным платежным поручениям

        :return: Ошибки по незагруженным платежным поручениям
        """
        return self.__errors


class ModulbankClient:
    """
    МодульБанк для Python-разработчиков.
    """
    api_url = "https://api.modulbank.ru/v1/"

    def __init__(self, token, sandbox_mode=False, page_size: int = 50):
        """
        Конструктор

        :param token: Токен из Личного Кабинета пользователя МодульБанка.
        :param sandbox_mode: Нужен ли `режим песочницы`
        :param page_size: Размер страницы операций, в штуках. От 0 до 50.
        """
        self.__token = token
        self.__sandbox_mode = sandbox_mode
        self.__headers = {'Authorization': 'Bearer ' + self.__token}
        if self.__sandbox_mode:
            self.__headers['sandbox'] = 'on'
        if page_size > 50:  # TODO: развязать местный page_size и records в API
            raise ValueError('page_size превышает допустимый предел в 50: %d' % page_size)
        self.__page_size = page_size

    def __str__(self):
        return "<ModulbankClient token='…' sandbox_mode='{sandbox_mode}' page_size={page_size}>".format(
            sandbox_mode=self.__sandbox_mode, page_size=self.__page_size)

    def accounts(self) -> []:
        """
        Получение информации о компаниях пользователя

        Метод в API: https://api.modulbank.ru/v1/account-info

        :return: Массив компаний, представленных структурой :class:`Company`
        """
        r = requests.post(self.api_url + 'account-info', json={}, headers=self.__headers)
        if r.status_code == 401:
            raise NotAuthorizedModulbankException()
        if r.status_code != 200:
            raise UnexpectedResponseStatusModulbankException(r.status_code)
        try:
            res = [Company(x) for x in r.json()]
        except ValueError:
            raise UnexpectedResponseBodyModulbankException(r.text)
        return res

    def balance(self, account_id: str) -> Decimal:
        """
        Получение баланса по счёту

        Метод в API: https://api.modulbank.ru/v1/account-info/balance/<bankAccountId>

        :param account_id: Системный идентификатор счёта
        :return: :class:`Decimal` Сумма остатка денежных средств на счёте
        """
        r = requests.post(self.api_url + 'account-info/balance/{id}'.format(id=account_id), json={},
                          headers=self.__headers)
        if r.status_code == 401:
            raise NotAuthorizedModulbankException()
        if r.status_code != 200:
            raise UnexpectedResponseStatusModulbankException(r.status_code)
        try:
            res = Decimal(r.text)
        except InvalidOperation:
            raise UnexpectedValueModulbankException('Balance %s as Decimal' % r.text)
        return res

    def operations(self, account_id: str, search: SearchOptions = SearchOptions()) -> []:
        """
        Просмотр истории операций

        Метод в API: https://api.modulbank.ru/v1/operation-history/<bankAccountId>

        :param account_id: Системный идентификатор счёта
        :param search: :class:`SearchOptions` Опциональные параметры поиска операций
        :return: Массив операций, представленных структурой :class:`Operation`
        """
        criteria = self.__patch_paging(search.to_dict())
        r = requests.post(self.api_url + 'operation-history/{id}'.format(id=account_id),
                          json=criteria,
                          headers=self.__headers)
        try:
            res = [Operation(x) for x in r.json()]
        except ValueError:
            raise UnexpectedResponseBodyModulbankException(r.text)
        return res

    def __patch_paging(self, param):
        """
        Правка критериев поиска в плане пейджинга.

        :param param: Критерии поиска
        :return: Поправленные критерии поиска
        """
        if 'page' not in param:
            return param
        page = param['page']
        param['skip'] = page * self.__page_size
        param['records'] = self.__page_size
        del param['page']

        return param

    def create_payment_draft(self, order: PaymentOrder) -> PaymentResponse:
        """
        Создание ерновика платёжки.

        Все создаваемые через API платежные поручения имеют статус "Черновик". Подписание поручений возможно только
        внутри личного кабинета.

        :return: `PaymentResponse`
        """
        exchange = ClientBankExchange()
        # noinspection PyTypeChecker
        self.__fill_client_bank_exchange(order, exchange)
        r = requests.post(self.api_url + 'operation-upload/1c', json={"document": exchange.document},
                          headers=self.__headers)
        if r.status_code != 200:
            raise UnexpectedResponseStatusModulbankException(r.status_code)
        return PaymentResponse(r.json())

    @staticmethod
    def __fill_client_bank_exchange(order, exchange):
        exchange.УсловияОтбора.РасчСчет = order.account_num
        exchange.СекцияПлатежногоДокумента.Номер = order.doc_num
        exchange.СекцияПлатежногоДокумента.Дата = order.date
        exchange.СекцияПлатежногоДокумента.Сумма = order.amount
        exchange.СекцияПлатежногоДокумента.НазначениеПлатежа = order.purpose

        exchange.СекцияПлатежногоДокумента.Плательщик1 = order.payer.name
        exchange.СекцияПлатежногоДокумента.ПлательщикИНН = order.payer.inn
        exchange.СекцияПлатежногоДокумента.ПлательщикКПП = order.payer.kpp
        exchange.СекцияПлатежногоДокумента.ПлательщикСчет = order.payer.bank.account
        exchange.СекцияПлатежногоДокумента.ПлательщикБанк1 = order.payer.bank.name
        exchange.СекцияПлатежногоДокумента.ПлательщикБИК = order.payer.bank.bic
        exchange.СекцияПлатежногоДокумента.ПлательщикКорсчет = order.payer.bank.corr_acc

        exchange.СекцияПлатежногоДокумента.Получатель1 = order.recipient.name
        exchange.СекцияПлатежногоДокумента.ПолучательИНН = order.recipient.inn
        exchange.СекцияПлатежногоДокумента.ПолучательКПП = order.recipient.kpp
        exchange.СекцияПлатежногоДокумента.ПолучательСчет = order.recipient.bank.account
        exchange.СекцияПлатежногоДокумента.ПолучательБанк1 = order.recipient.bank.name
        exchange.СекцияПлатежногоДокумента.ПолучательБИК = order.recipient.bank.bic
        exchange.СекцияПлатежногоДокумента.ПолучательКорсчет = order.recipient.bank.corr_acc

        exchange.СекцияПлатежногоДокумента.ВидОплаты = order.payment_type
        exchange.СекцияПлатежногоДокумента.Очередность = order.priority
        exchange.СекцияПлатежногоДокумента.ДатаСписано = order.date
