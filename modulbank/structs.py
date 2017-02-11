import datetime
import hashlib
from decimal import Decimal, InvalidOperation
from enum import Enum

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

    def __init__(self, obj: {}):
        """
        Конструктор

        :param obj: JSON-объект компании из API МодульБанка.
        """
        if 'companyId' in obj:
            self.__company_id = obj['companyId']
        if 'companyName' in obj:
            self.__name = obj['companyName']
        if 'bankAccounts' in obj:
            self.__bank_accounts = [BankAccount(x) for x in obj['bankAccounts']]

    def __str__(self):
        return "<Company name={s.name} id={s.company_id}>".format(s=self)

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

    def __init__(self, obj: {}):
        """
        Конструктор

        :param obj: JSON-объект банковского счёта (!) из API МодульБанка.
        """
        if 'bankBic' in obj:
            self.__bic = obj['bankBic']
        if 'bankInn' in obj:
            self.__inn = obj['bankInn']
        if 'bankKpp' in obj:
            self.__kpp = obj['bankKpp']
        if 'bankCorrespondentAccount' in obj:
            self.__corr_acc = obj['bankCorrespondentAccount']
        if 'bankName' in obj:
            self.__name = obj['bankName']

    def __str__(self):
        return "<Bank БИК={s.bic} ИНН={s.inn} КПП={s.kpp} name={s.name} к/сч={s.corr_account}>".format(s=self)

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

    def __init__(self, obj: {}):
        """
        Конструктор

        :param obj: JSON-объект банковского счёта из API МодульБанка.
        """
        if 'id' in obj:
            self.__account_id = obj['id']
        if 'accountName' in obj:
            self.__name = obj['accountName']
        if 'balance' in obj:
            try:
                self.__balance = Decimal(obj['balance'])
            except InvalidOperation:
                raise UnexpectedValueModulbankException('Balance %s as Decimal' % obj['balance'])
        if 'beginDate' in obj:
            try:
                self.__begin_date = datetime.datetime.strptime(obj['beginDate'], '%Y-%m-%dT%H:%M:%S').date()
            except ValueError:
                raise UnexpectedValueModulbankException('BeginDate %s as datetime.date' % obj['beginDate'])
        if 'category' in obj:
            try:
                self.__category = AccountCategory[obj['category']]
            except KeyError:
                raise UnexpectedValueModulbankException('AccountCategory %s as AccountCategory' % obj['category'])
        if 'currency' in obj:
            try:
                self.__currency = Currency[obj['currency']]
            except KeyError:
                raise UnexpectedValueModulbankException('Currency %s as Currency' % obj['currency'])
        if 'number' in obj:
            self.__number = obj['number']
        if 'status' in obj:
            try:
                self.__status = AccountStatus[obj['status']]
            except KeyError:
                raise UnexpectedValueModulbankException('AccountStatus %s as AccountStatus' % obj['status'])
        if 'bankBic' in obj or 'bankInn' in obj or 'bankKpp' in obj or 'bankCorrespondentAccount' in obj \
                or 'bankName' in obj:
            self.__bank = Bank(obj)

    def __str__(self):
        return "<BankAccount name={s.name} id={s.account_id} balance={s.balance} beginDate={s.begin_date} " \
               "category={s.category} currency={s.currency} number={s.number} status={s.status} \n" \
               "bank= {s.bank}>".format(s=self)

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

    def __init__(self, account=None, name=None, bic=None, corr_acc=None):
        """
        Конструктор

        :param account: Номер счета
        :param name: Название банка
        :param bic: БИК
        :param corr_acc: Корр. счёт
        """
        self.__account = account
        self.__name = name
        self.__bic = bic
        self.__corr_acc = corr_acc

    def __str__(self):
        s = "<BankShort account={s.account} name={s.name} bic={s.bic}{corr_acc}>" \
            .format(s=self, corr_acc=self.corr_acc and " к/сч=" + self.corr_acc or '')
        return s

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

    def __init__(self, obj: dict = None, name=None, inn=None, kpp=None, bank=None):
        """
        Конструктор

        :param obj: JSON-объект операции по счёту из API МодульБанка.
        :param name:
        :param inn:
        :param kpp:
        :param bank:
        """
        if obj:
            if 'contragentName' in obj:
                self.__name = obj['contragentName']
            if 'contragentInn' in obj:
                self.__inn = obj['contragentInn']
            if 'contragentKpp' in obj:
                self.__kpp = obj['contragentKpp']
            if 'contragentBankAccountNumber' in obj or 'contragentBankName' in obj or 'contragentBankBic' in obj:
                self.__bank = BankShort(account=obj['contragentBankAccountNumber'] or None,
                                        name=obj['contragentBankName'] or None,
                                        bic=obj['contragentBankBic'] or None)
        else:
            self.__name = name
            self.__inn = inn
            self.__kpp = kpp
            self.__bank = bank

    def __str__(self):
        return "<Contractor name={s.name} inn={s.inn} kpp={s.kpp} bank:{s.bank}>".format(s=self)

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
        return self.__kpp or '0'

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

    def __init__(self, obj: {}):
        """
        Конструктор

        :param obj: JSON-объект операции по счёту из API МодульБанка.
        """
        if 'kbk' in obj:
            self.__kbk = obj['kbk']
        if 'oktmo' in obj:
            self.__oktmo = obj['oktmo']
        if 'paymentBasis' in obj:
            self.__payment_basis = obj['paymentBasis']
        if 'taxCode' in obj:
            self.__tax_code = obj['taxCode']
        if 'taxDocNum' in obj:
            self.__tax_doc_num = obj['taxDocNum']
        if 'taxDocDate' in obj:
            self.__tax_doc_date = obj['taxDocDate']
        if 'payerStatus' in obj:
            self.__payer_status = obj['payerStatus']
        if 'uin' in obj:
            self.__uin = obj['uin']

    def __str__(self):
        s = "<BudgetaryAndTax{kbk}{oktmo}{payment_basis}{tax_code}{tax_doc_num}{tax_doc_date}{payer_status}" \
            "{uin}>".format(kbk=self.kbk and ' kbk=' + self.kbk or '',
                            oktmo=self.oktmo and ' oktmo=' + self.oktmo or '',
                            payment_basis=self.payment_basis and ' payment_basis=' + self.payment_basis or '',
                            tax_code=self.tax_code and ' tax_code=' + self.tax_code or '',
                            tax_doc_num=self.tax_doc_num and ' tax_doc_num=' + self.tax_doc_num or '',
                            tax_doc_date=self.tax_doc_date and ' tax_doc_date=' + self.tax_doc_date or '',
                            payer_status=self.payer_status and ' payer_status=' + self.payer_status or '',
                            uin=self.uin and ' uin=' + self.uin or '')
        return s

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

    def __init__(self, obj: {}):
        """
        Конструктор

        :param obj: JSON-объект операции по счёту из API МодульБанка.
        """
        if 'id' in obj:
            self.__operation_id = obj['id']
        if 'companyId' in obj:
            self.__company_id = obj['companyId']
        if 'status' in obj:
            try:
                self.__status = OperationStatus[obj['status']]
            except KeyError:
                raise UnexpectedValueModulbankException('OperationStatus %s as OperationStatus' % obj['status'])
        if 'category' in obj:
            try:
                self.__category = OperationCategory[obj['category']]
            except KeyError:
                raise UnexpectedValueModulbankException('OperationCategory %s as OperationCategory' % obj['category'])
        if 'currency' in obj:
            try:
                self.__currency = Currency[obj['currency']]
            except KeyError:
                raise UnexpectedValueModulbankException('Currency %s as Currency' % obj['currency'])
        if 'amount' in obj:
            try:
                self.__amount = Decimal(obj['amount'])
            except InvalidOperation:
                raise UnexpectedValueModulbankException('Amount %s as Decimal' % obj['amount'])
        if 'amountWithCommission' in obj:
            try:
                self.__amount_with_commission = Decimal(obj['amountWithCommission'])
            except InvalidOperation:
                raise UnexpectedValueModulbankException(
                    'AmountWithCommission %s as Decimal' % obj['amountWithCommission'])
        if 'bankAccountNumber' in obj:
            self.__account_number = obj['bankAccountNumber']
        if 'paymentPurpose' in obj:
            self.__purpose = obj['paymentPurpose']
        if 'executed' in obj:
            try:
                self.__executed = datetime.datetime.strptime(obj['executed'], '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                raise UnexpectedValueModulbankException('Executed %s as datetime.datetime' % obj['executed'])
        if 'created' in obj:
            try:
                self.__created = datetime.datetime.strptime(obj['created'], '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                raise UnexpectedValueModulbankException('Created %s as datetime.datetime' % obj['created'])
        if 'docNumber' in obj:
            self.__doc_number = obj['docNumber']
        if 'contragentName' in obj or 'contragentInn' in obj or 'contragentKpp' in obj \
                or 'contragentBankAccountNumber' in obj or 'contragentBankName' in obj or 'contragentBankBic' in obj:
            self.__contractor = Contractor(obj)
        if 'kbk' in obj or 'oktmo' in obj or 'paymentBasis' in obj or 'taxCode' in obj or 'taxDocNum' in obj \
                or 'taxDocDate' in obj or 'payerStatus' in obj or '	' in obj:
            self.__budgetary_and_tax = BudgetaryAndTax(obj)
        else:
            self.__budgetary_and_tax = None

    def __str__(self):
        return "<Operation operation_id={s.operation_id} company_id={s.company_id} status={s.status} " \
               "category={s.category} currency={s.currency} amount={s.amount} " \
               "amount_with_commission={s.amount_with_commission} account_number={s.account_number} " \
               "purpose={s.purpose} executed={s.executed} created={s.created} doc_number={s.doc_number} " \
               "contractor:{s.contractor}{budgetary_and_tax}>" \
            .format(s=self,
                    budgetary_and_tax=self.budgetary_and_tax and "budgetary_and_tax:" + str(
                        self.budgetary_and_tax) or '')

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

        :param doc_num: Номер документа
        :param account_num: Расчетный счет организации
        :param amount: Сумма платежа
        :param purpose: Назначение платежа одной строкой
        :param payer: Плательщик :class:`Contractor` и его реквизиты
        :param recipient: Получатель :class:`Contractor` и его реквизиты
        :param payment_type: (опционально) Вид оплаты (вид операции). Для платежных поручений всегда 01
        :param priority: (опционально) Очередность платежа. Для обычных операций всегда 5
        :param date: (опционально) Дата списания средств с р/c. По умолчанию сегодняшнее число
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

        :param obj: JSON-объект уведомления о произошедшей транзакции из API МодульБанка.
        """
        self.__inn = 'companyInn' in obj and obj['companyInn'] or ''
        self.__kpp = 'contragentKpp' in obj and obj['contragentKpp'] or ''
        if 'operation' in obj:
            self.__operation = Operation(obj['operation'])
        if 'SHA1Hash' in obj:
            self.__signature = obj['SHA1Hash']

    def __str__(self):
        return "<NotifyRequest inn={s.inn} kpp={s.kpp} operation:{s.operation} signature={s.signature}>".format(s=self)

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
