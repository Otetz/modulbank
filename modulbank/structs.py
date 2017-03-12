import datetime
import hashlib
from decimal import Decimal, InvalidOperation
from enum import Enum

import pytz

from .exceptions import UnexpectedValueModulbankException

AccountCategory = Enum('AccountCategory',
                       'CheckingAccount DepositAccount CardAccount DepositRateAccount ReservationAccounting')
Currency = Enum('Currency', 'RUR USD EUR CNY')
AccountStatus = Enum('AccountStatus', 'New Deleted Closed Freezed ToClosed ToOpen')
OperationStatus = Enum('OperationStatus', 'SendToBank Executed RejectByBank Canceled Received')
OperationCategory = Enum('OperationCategory', 'Debet Credit')


class Company:
    """
    Компания, в которой состоит пользователь МодульБанка.
    """

    def __init__(self, obj: dict):
        """
        Конструктор

        :param dict obj: JSON-объект компании из API МодульБанка.
        """
        self.__company_id = obj.get('companyId')
        self.__name = obj.get('companyName')
        self.__bank_accounts = [BankAccount(x) for x in obj.get('bankAccounts', [])]

    def __str__(self):
        return ('<%s ' % self.__class__.__name__) + ' '.join(
            ['%s:%s' % (k.replace('_' + self.__class__.__name__, '').lstrip('_'), str(self.__dict__[k]))
             for k in self.__dict__]) + '>'

    @property
    def company_id(self) -> str:
        """
        Системный идентификатор компании

        :return: Системный идентификатор компании
        :rtype: str
        """
        return self.__company_id

    @property
    def name(self) -> str:
        """
        Название компании

        :return: Название компании
        :rtype: str
        """
        return self.__name

    @property
    def bank_accounts(self) -> list:
        """
        Массив счетов компании

        :return: Массив счетов компании
        :rtype: list(BankAccount)
        """
        return self.__bank_accounts


class Bank:
    """
    Реквизиты банка (из платежных реквизитов организации).
    """

    def __init__(self, obj: dict):
        """
        Конструктор

        :param dict obj: JSON-объект банковского счёта (!) из API МодульБанка.
        """
        self.__bic = obj.get('bankBic')
        self.__inn = obj.get('bankInn')
        self.__kpp = obj.get('bankKpp')
        self.__corr_acc = obj.get('bankCorrespondentAccount')
        self.__name = obj.get('bankName')

    def __str__(self):
        names = {'bic': 'БИК', 'inn': 'ИНН', 'kpp': 'КПП', 'corr_acc': 'к/сч'}
        return ('<%s ' % self.__class__.__name__) + ' '.join(
            ['%s:%s' % (names.get(k.replace('_' + self.__class__.__name__, '').lstrip('_'),
                                  k.replace('_' + self.__class__.__name__, '').lstrip('_')), str(self.__dict__[k]))
             for k in self.__dict__]) + '>'

    @property
    def bic(self) -> str:
        """
        БИК Банка

        :return: БИК Банка
        :rtype: str
        """
        return self.__bic

    @property
    def inn(self) -> str:
        """
        ИНН Банка

        :return: ИНН Банка
        :rtype: str
        """
        return self.__inn

    @property
    def kpp(self) -> str:
        """
        КПП Банка

        :return: КПП Банка
        :rtype: str
        """
        return self.__kpp

    @property
    def name(self) -> str:
        """
        Наименование банка

        :return: Наименование банка
        :rtype: str
        """
        return self.__name

    @property
    def corr_account(self) -> str:
        """
        Номер корреспондетского счёта

        :return: Корр. счёт
        :rtype: str
        """
        return self.__corr_acc


class BankAccount:
    """
    Счёт компании-пользователя МодульБанка.
    """

    def __init__(self, obj: dict):
        """
        Конструктор

        :param dict obj: JSON-объект банковского счёта из API МодульБанка.
        """
        self.__account_id = obj.get('id')
        self.__name = obj.get('accountName')
        try:
            self.__balance = Decimal(obj.get('balance'))
        except InvalidOperation:
            raise UnexpectedValueModulbankException('Balance %s as Decimal' % obj.get('balance'))
        try:
            self.__begin_date = obj.get('beginDate') and datetime.datetime.strptime(obj.get('beginDate'),
                                                                                    '%Y-%m-%dT%H:%M:%S').date() or None
        except ValueError:
            raise UnexpectedValueModulbankException('BeginDate %s as datetime.date' % obj.get('beginDate'))
        try:
            self.__category = AccountCategory[obj.get('category')]
        except KeyError:
            raise UnexpectedValueModulbankException('AccountCategory %s as AccountCategory' % obj.get('category'))
        try:
            self.__currency = Currency[obj.get('currency')]
        except KeyError:
            raise UnexpectedValueModulbankException('Currency %s as Currency' % obj.get('currency'))
        self.__number = obj.get('number')
        try:
            self.__status = AccountStatus[obj.get('status')]
        except KeyError:
            raise UnexpectedValueModulbankException('AccountStatus %s as AccountStatus' % obj.get('status'))
        if 'bankBic' in obj or 'bankInn' in obj or 'bankKpp' in obj or 'bankCorrespondentAccount' in obj \
                or 'bankName' in obj:
            self.__bank = Bank(obj)

    def __str__(self):
        return ('<%s ' % self.__class__.__name__) + ' '.join(
            ['%s:%s' % (k.replace('_' + self.__class__.__name__, '').lstrip('_'), str(self.__dict__[k]))
             for k in self.__dict__]) + '>'

    @property
    def account_id(self) -> str:
        """
        Системный идентификатор счёта

        :return: Системный идентификатор счёта
        :rtype: str
        """
        return self.__account_id

    @property
    def name(self) -> str:
        """
        Наименование счёта

        :return: Наименование счёта
        :rtype: str
        """
        return self.__name

    @property
    def balance(self) -> Decimal:
        """
        Баланс на счёте

        :return: Баланс на счёте (в валюте счёта)
        :rtype: Decimal
        """
        return self.__balance

    @property
    def begin_date(self) -> datetime.date:
        """
        Дата открытия счёта

        :return: Дата открытия счёта
        :rtype: datetime.date
        """
        return self.__begin_date

    @property
    def category(self) -> AccountCategory:
        """
        Категория счёта

        Возможные значения:

         - CheckingAccount (расчетный счёт),
         - DepositAccount (депозитный счёт),
         - CardAccount (карточный счёт),
         - DepositRateAccount (счёт для процентов по депозиту),
         - ReservationAccounting (счёт учета резервов)

        :return: Категория счёта
        :rtype: AccountCategory
        """
        return self.__category

    @property
    def currency(self) -> Currency:
        """
        Код валюты

        Возможные значения:

         - RUR
         - USD
         - EUR
         - CNY

        :return: Код валюты
        :rtype: Currency
        """
        return self.__currency

    @property
    def number(self) -> str:
        """
        Номер счёта

        :return: Номер счёта
        :rtype: str
        """
        return self.__number

    @property
    def status(self) -> AccountStatus:
        """
        Состояния счёта

        Возможные значения:

         - New (открытый)
         - Deleted (удалённый)
         - Closed (закрытый)
         - Freezed (замороженный)
         - ToClosed (в процессе закрытия)
         - ToOpen (в процессе открытия)

        :return: Состояние счёта
        :rtype: AccountStatus
        """
        return self.__status

    @property
    def bank(self) -> Bank:
        """
        Реквизиты банка

        :return: Реквизиты банка
        :rtype: Bank
        """
        return self.__bank


class BankShort:
    """
    Короткие банковские реквизиты.

    Номер счета, Название банка, БИК и корр. счёт.
    """

    def __init__(self, account: str = None, name: str = None, bic: str = None, corr_acc: str = None):
        """
        Конструктор

        :param str account: Номер счета
        :param str name: Название банка
        :param str bic: БИК
        :param str corr_acc: Корр. счёт
        """
        self.__account = account
        self.__name = name
        self.__bic = bic
        self.__corr_acc = corr_acc

    def __str__(self):
        return ('<%s ' % self.__class__.__name__) + ' '.join(
            ['%s:%s' % (k.replace('_' + self.__class__.__name__, '').lstrip('_'), str(self.__dict__[k]))
             for k in self.__dict__]) + '>'

    @property
    def account(self) -> str:
        """
        Номер счета

        :return: Номер счета
        :rtype: str
        """
        return self.__account

    @property
    def name(self) -> str:
        """
        Название банка

        :return: Название банка
        :rtype: str
        """
        return self.__name

    @property
    def bic(self) -> str:
        """
        БИК

        :return: БИК
        :rtype: str
        """
        return self.__bic

    @property
    def corr_acc(self) -> str:
        """
        Корреспондентский счёт

        :return: Корреспондентский счёт
        :rtype: str
        """
        return self.__corr_acc


class Contractor:
    """
    Контрагент в операции.
    """

    def __init__(self, obj: dict = None, name: str = None, inn: str = None, kpp: str = None, bank: BankShort = None):
        """
        Конструктор

        :param dict obj: JSON-объект операции по счёту из API МодульБанка.
        :param str name:
        :param str inn:
        :param str kpp:
        :param BankShort bank:
        """
        if obj:
            self.__name = obj.get('contragentName')
            self.__inn = obj.get('contragentInn')
            self.__kpp = obj.get('contragentKpp')
            if 'contragentBankAccountNumber' in obj or 'contragentBankName' in obj or 'contragentBankBic' in obj:
                self.__bank = BankShort(account=obj.get('contragentBankAccountNumber'),
                                        name=obj.get('contragentBankName'),
                                        bic=obj.get('contragentBankBic'))
        else:
            self.__name = name
            self.__inn = inn
            self.__kpp = kpp
            self.__bank = bank

    def __str__(self):
        return ('<%s ' % self.__class__.__name__) + ' '.join(
            ['%s:%s' % (k.replace('_' + self.__class__.__name__, '').lstrip('_'), str(self.__dict__[k]))
             for k in self.__dict__]) + '>'

    @property
    def name(self) -> str:
        """
        Полное наименование контрагента

        :return: Полное наименование контрагента
        :rtype: str
        """
        return self.__name

    @property
    def inn(self) -> str:
        """
        ИНН контрагента

        :return: ИНН контрагента
        :rtype: str
        """
        return self.__inn

    @property
    def kpp(self) -> str:
        """
        КПП контрагента

        :return: КПП контрагента
        :rtype: str
        """
        return self.__kpp

    @property
    def bank(self) -> BankShort:
        """
        Банковские реквизиты контрагента (Номер счета, Название банка и БИК)

        :return: Банковские реквизиты контрагента
        :rtype: BankShort
        """
        return self.__bank


class BudgetaryAndTax:
    """
    Параметры бюджетных и налоговых платежей в операции.
    """

    def __init__(self, obj: dict):
        """
        Конструктор

        :param dict obj: JSON-объект операции по счёту из API МодульБанка.
        """
        self.__kbk = obj.get('kbk')
        self.__oktmo = obj.get('oktmo')
        self.__payment_basis = obj.get('paymentBasis')
        self.__tax_code = obj.get('taxCode')
        self.__tax_doc_num = obj.get('taxDocNum')
        self.__tax_doc_date = obj.get('taxDocDate')
        self.__payer_status = obj.get('payerStatus')
        self.__uin = obj.get('uin')

    def __str__(self):
        return ('<%s ' % self.__class__.__name__) + ' '.join(
            ['%s:%s' % (k.replace('_' + self.__class__.__name__, '').lstrip('_'), str(self.__dict__[k]))
             for k in self.__dict__]) + '>'

    @property
    def kbk(self) -> str:
        """
        Код бюджетной классификации (104)

        :return: Код бюджетной классификации
        :rtype: str
        """
        return self.__kbk

    @property
    def oktmo(self) -> str:
        """
        Общероссийский классификатор территорий муниципальных образований (105)

        :return: Общероссийский классификатор территорий муниципальных образований
        :rtype: str
        """
        return self.__oktmo

    @property
    def payment_basis(self) -> str:
        """
        Основание платежа (106)

        :return: Основание платежа
        :rtype: str
        """
        return self.__payment_basis

    @property
    def tax_code(self) -> str:
        """
        Налоговый период

        :return: Налоговый период
        :rtype: str
        """
        return self.__tax_code

    @property
    def tax_doc_num(self) -> str:
        """
        Номер документа (108)

        :return: Номер документа
        :rtype: str
        """
        return self.__tax_doc_num

    @property
    def tax_doc_date(self) -> str:
        """
        Дата документа (109)

        :return: Дата документа
        :rtype: str
        """
        return self.__tax_doc_date

    @property
    def payer_status(self) -> str:
        """
        Статус плательщика (101)

        :return: Статус плательщика
        :rtype: str
        """
        return self.__payer_status

    @property
    def uin(self) -> str:
        """
        Уникальный идентификатор начисления (22)

        :return: Уникальный идентификатор начисления
        :rtype: str
        """
        return self.__uin


class Operation:
    """
    Операция по счёту
    """

    def __init__(self, obj: dict):
        """
        Конструктор

        :param dict obj: JSON-объект операции по счёту из API МодульБанка.
        """
        self.__operation_id = obj.get('id')
        self.__company_id = obj.get('companyId')
        try:
            self.__status = OperationStatus[obj.get('status')]
        except KeyError:
            raise UnexpectedValueModulbankException('OperationStatus %s as OperationStatus' % obj.get('status'))
        try:
            self.__category = OperationCategory[obj.get('category')]
        except KeyError:
            raise UnexpectedValueModulbankException('OperationCategory %s as OperationCategory' % obj.get('category'))
        try:
            self.__currency = Currency[obj.get('currency')]
        except KeyError:
            raise UnexpectedValueModulbankException('Currency %s as Currency' % obj.get('currency'))
        try:
            self.__amount = Decimal(obj.get('amount'))
        except InvalidOperation:
            raise UnexpectedValueModulbankException('Amount %s as Decimal' % obj.get('amount'))
        try:
            self.__amount_with_commission = Decimal(obj.get('amountWithCommission'))
        except InvalidOperation:
            raise UnexpectedValueModulbankException(
                'AmountWithCommission %s as Decimal' % obj.get('amountWithCommission'))
        self.__account_number = obj.get('bankAccountNumber')
        self.__purpose = obj.get('paymentPurpose')
        try:
            self.__executed = obj.get('executed') and datetime.datetime.strptime(obj.get('executed'),
                                                                                 '%Y-%m-%dT%H:%M:%S').replace(tzinfo=pytz.timezone('Europe/Moscow')) or None
        except ValueError:
            raise UnexpectedValueModulbankException('Executed %s as datetime.datetime' % obj.get('executed'))
        try:
            self.__created = obj.get('created') and datetime.datetime.strptime(obj.get('created'),
                                                                               '%Y-%m-%dT%H:%M:%S').replace(tzinfo=pytz.timezone('Europe/Moscow')) or None
        except ValueError:
            try:
                self.__created = obj.get('created') and datetime.datetime.strptime(obj.get('created'),
                                                                                   '%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=pytz.timezone('Europe/Moscow')) or None
            except ValueError:
                raise UnexpectedValueModulbankException('Created %s as datetime.datetime' % obj.get('created'))
        self.__doc_number = obj.get('docNumber')
        if 'contragentName' in obj or 'contragentInn' in obj or 'contragentKpp' in obj \
                or 'contragentBankAccountNumber' in obj or 'contragentBankName' in obj or 'contragentBankBic' in obj:
            self.__contractor = Contractor(obj)
        if 'kbk' in obj or 'oktmo' in obj or 'paymentBasis' in obj or 'taxCode' in obj or 'taxDocNum' in obj \
                or 'taxDocDate' in obj or 'payerStatus' in obj or '	' in obj:
            self.__budgetary_and_tax = BudgetaryAndTax(obj)
        else:
            self.__budgetary_and_tax = None

    def __str__(self):
        return ('<%s ' % self.__class__.__name__) + ' '.join(
            ['%s:%s' % (k.replace('_' + self.__class__.__name__, '').lstrip('_'), str(self.__dict__[k]))
             for k in self.__dict__]) + '>'

    @property
    def operation_id(self) -> str:
        """
        Системный идентификатор транзакции

        :return: Системный идентификатор транзакции
        :rtype: str
        """
        return self.__operation_id

    @property
    def company_id(self) -> str:
        """
        Системный идентификатор компании

        :return: Системный идентификатор компании
        :rtype: str
        """
        return self.__company_id

    @property
    def status(self) -> OperationStatus:
        """
        Текущий статус транзакции.

        Возможные значения:

         - SendToBank (Исходящая, ожидающая исполнения),
         - Executed (Исходящий исполненный),
         - RejectByBank (Исходящая, отказано банком в исполнении),
         - Canceled (Исходящая, отправленная в банк и отменённая пользователем),
         - Received (Входящая исполненная)

        :return: Текущий статус транзакции
        :rtype: OperationStatus
        """
        return self.__status

    @property
    def category(self) -> OperationCategory:
        """
        Направление платежа.

        Возможные значения:

         - Debet (входящая),
         - Credit (исходящая)

        :return: Направление платежа
        :rtype: OperationCategory
        """
        return self.__category

    @property
    def currency(self) -> Currency:
        """
        Код валюты.

        Возможные значения:

         - RUR,
         - EUR,
         - USD,
         - CNY

        :return: Код валюты
        :rtype: Currency
        """
        return self.__currency

    @property
    def amount(self) -> Decimal:
        """
        Сумма платежа без учета банковской комиссии

        :return: Сумма платежа без учета банковской комиссии
        :rtype: Decimal
        """
        return self.__amount

    @property
    def amount_with_commission(self) -> Decimal:
        """
        Сумма платежа с учетом банковской комиссии

        :return: Сумма платежа с учетом банковской комиссии
        :rtype: Decimal
        """
        return self.__amount_with_commission

    @property
    def account_number(self) -> str:
        """
        Номер банковского счета

        :return: Номер банковского счета
        :rtype: str
        """
        return self.__account_number

    @property
    def purpose(self) -> str:
        """
        Назначение платежа

        :return: Назначение платежа
        :rtype: str
        """
        return self.__purpose

    @property
    def executed(self) -> datetime.datetime:
        """
        Дата проведения платежа

        :return: Дата проведения платежа
        :rtype: datetime.datetime
        """
        return self.__executed

    @property
    def created(self) -> datetime.datetime:
        """
        Дата создания транзакции

        :return: Дата создания транзакции
        :rtype: datetime.datetime
        """
        return self.__created

    @property
    def doc_number(self) -> str:
        """
        Номер документа

        :return: Номер документа
        :rtype: str
        """
        return self.__doc_number

    @property
    def contractor(self) -> Contractor:
        """
        Контрагент

        :return: Контрагент
        :rtype: Contractor
        """
        return self.__contractor

    @property
    def budgetary_and_tax(self) -> BudgetaryAndTax:
        """
        Параметры бюджетных и налоговых платежей в операции

        :return:  Параметры бюджетных и налоговых платежей в операции
        :rtype: BudgetaryAndTax
        """
        return self.__budgetary_and_tax


class PaymentOrder:
    """
    Платёжное поручение
    """

    def __init__(self, doc_num: str, account_num: str, amount: Decimal, purpose: str, payer: Contractor,
                 recipient: Contractor, payment_type: str = '01', priority: str = '5', date: datetime.date = None):
        """
        Конструктор

        :param str doc_num: Номер документа
        :param str account_num: Расчетный счет организации
        :param Decimal amount: Сумма платежа
        :param str purpose: Назначение платежа одной строкой
        :param Contractor payer: Плательщик :class:`Contractor` и его реквизиты
        :param Contractor recipient: Получатель :class:`Contractor` и его реквизиты
        :param str payment_type: (опционально) Вид оплаты (вид операции). Для платежных поручений всегда 01
        :param str priority: (опционально) Очередность платежа. Для обычных операций всегда 5
        :param datetime.date date: (опционально) Дата списания средств с р/c. По умолчанию сегодняшнее число
        """
        self.__doc_num = doc_num
        self.__account_num = account_num
        self.__amount = amount
        self.__purpose = purpose
        self.__payer = payer
        self.__recipient = recipient
        self.__type = payment_type
        self.__priority = priority
        self.__date = date is not None and date or datetime.date.today()

    def __str__(self):
        return ('<%s ' % self.__class__.__name__) + ' '.join(
            ['%s:%s' % (k.replace('_' + self.__class__.__name__, '').lstrip('_'), str(self.__dict__[k]))
             for k in self.__dict__]) + '>'

    @property
    def doc_num(self) -> str:
        """
        Номер документа

        :return: Номер документа
        :rtype: str
        """
        return self.__doc_num

    @property
    def account_num(self) -> str:
        """
        Номер банковского счета

        :return: Номер банковского счета
        :rtype: str
        """
        return self.__account_num

    @property
    def amount(self) -> Decimal:
        """
        Сумма платежа

        :return: Сумма платежа
        :rtype: Decimal
        """
        return self.__amount

    @property
    def purpose(self) -> str:
        """
        Назначение платежа

        :return: Назначение платежа
        :rtype: str
        """
        return self.__purpose

    @property
    def payer(self) -> Contractor:
        """
        Плательщик

        :return: Плательщик
        :rtype: Contractor
        """
        return self.__payer

    @property
    def recipient(self) -> Contractor:
        """
        Получатель

        :return: Получатель
        :rtype: Contractor
        """
        return self.__recipient

    @property
    def payment_type(self) -> str:
        """
        Вид оплаты. По умолчанию '01'.

        :return: Вид оплаты
        :rtype: str
        """
        return self.__type

    @property
    def priority(self) -> str:
        """
        Очередность. По умолчанию '5'.

        :return: Очередность
        :rtype: str
        """
        return self.__priority

    @property
    def date(self) -> datetime.date:
        """
        Дата подготовки платежа

        :return: Дата подготовки платежа
        :rtype: datetime.date
        """
        return self.__date


class NotifyRequest:
    """
    Уведомление о произошедшей транзакции.
    """

    def __init__(self, obj: dict = None):
        """
        Конструктор

        :param dict obj: JSON-объект уведомления о произошедшей транзакции из API МодульБанка.
        """
        self.__inn = obj.get('companyInn', '')
        self.__kpp = obj.get('contragentKpp', '')
        self.__operation = Operation(obj.get('operation'))
        self.__signature = obj.get('SHA1Hash')

    def __str__(self):
        return ('<%s ' % self.__class__.__name__) + ' '.join(
            ['%s:%s' % (k.replace('_' + self.__class__.__name__, '').lstrip('_'), str(self.__dict__[k]))
             for k in self.__dict__]) + '>'

    @property
    def inn(self) -> str:
        """
        ИНН компании (для которой в Модульбанке появилась транзакция)

        :return: ИНН компании
        :rtype: str
        """
        return self.__inn

    @property
    def kpp(self) -> str:
        """
        КПП компании (для которой в Модульбанке появилась транзакция)

        :return: КПП компании
        :rtype: str
        """
        return self.__kpp

    @property
    def operation(self) -> Operation:
        """
        Операция по счёту

        :return: Операция по счёту
        :rtype: Operation
        """
        return self.__operation

    @property
    def signature(self) -> str:
        """
        Подпись сообщения, гарантирующая целостность данных уведомления и то, что уведомления были отправлены сервером
        Модульбанка. Проверяется с помощью :meth:`check_signature`

        :return: Подпись сообщения
        :rtype: str
        """
        return self.__signature

    def check_signature(self, token) -> bool:
        """
        Проверка SHA1-подписи.

        :param str token: Токен из ЛК МодульБанка
        :return: Успешность проверки цифровой подписи
        :rtype: bool
        """
        s = "{}&{}".format(token[:10], self.operation.operation_id)
        digest = hashlib.sha1(s.encode()).hexdigest()
        return digest.lower() == self.signature.lower()
