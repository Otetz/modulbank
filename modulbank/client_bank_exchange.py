import datetime

from decimal import Decimal, ROUND_HALF_DOWN

import pytz


class BaseSection:
    """
    Абстрактный базовый класс для секций документа обмена данными
    """
    _fields = []
    _mandatory_fields = []

    def __str__(self):
        s = ""
        for name in self._fields:
            s += "\t{}: {}\n".format(name, str(self.__dict__[name]))
        return s

    @property
    def document(self) -> str:
        """
        Свойство выдает полностью сформированную секцию документа в формате 1С.

        :return: Текст секции
        :rtype: str
        """
        s = ""
        for name in self._mandatory_fields:
            value = self.__dict__[name]
            if value is None:
                value = ''
            value = self.__format_value(value)
            s += "{}={}\n".format(name, value)
        for name in self._fields:
            if name in self._mandatory_fields or self.__dict__[name] is None:
                continue
            value = self.__dict__[name]
            value = self.__format_value(value)
            s += "{}={}\n".format(name, value)
        return s

    @staticmethod
    def __format_value(value) -> str:
        if isinstance(value, datetime.date):
            return value.strftime('%d.%m.%Y')
        if isinstance(value, datetime.time):
            return value.strftime('%H:%M:%S')
        if isinstance(value, Decimal):
            return str(value.quantize(Decimal('.01'), rounding=ROUND_HALF_DOWN))
        return value


class GeneralSection(BaseSection):
    """
    `Общая` секция
    """
    _fields = ['ВерсияФормата', 'Кодировка', 'Отправитель', 'Получатель', 'ДатаСоздания', 'ВремяСоздания']
    _mandatory_fields = ['ВерсияФормата', 'Кодировка', 'Отправитель']

    def __init__(self):
        BaseSection.__init__(self)

        for name in self._fields:
            self.__dict__[name] = None

        self.__dict__['ВерсияФормата'] = '1.02'
        self.__dict__['Кодировка'] = 'Windows'
        self.__dict__['Отправитель'] = 'modulbank_python'
        self.__dict__['ДатаСоздания'] = datetime.date.today()
        self.__dict__['ВремяСоздания'] = datetime.datetime.now().replace(tzinfo=pytz.timezone('Europe/Moscow')).time()


class FilterSection(BaseSection):
    """
    Секция `Фильтров`
    """
    _fields = ['ДатаНачала', 'ДатаКонца', 'РасчСчет', 'Документ']
    _mandatory_fields = ['ДатаНачала', 'ДатаКонца', 'РасчСчет']

    def __init__(self):
        BaseSection.__init__(self)

        for name in self._fields:
            self.__dict__[name] = None

        self.__dict__['ДатаНачала'] = datetime.date.today()
        self.__dict__['ДатаКонца'] = datetime.date.today()


class BalancesSection(BaseSection):
    """
    Секция `Начальных остатков`
    """
    _fields = ['ДатаНачала', 'ДатаКонца', 'РасчСчет', 'НачальныйОстаток', 'ВсегоПоступило', 'ВсегоСписано',
               'КонечныйОстаток']
    _mandatory_fields = []

    def __init__(self):
        BaseSection.__init__(self)

        for name in self._fields:
            self.__dict__[name] = None


class DocumentSection(BaseSection):
    """
    Секция `Документ`
    """
    _fields = ['Номер', 'Дата', 'Сумма', 'КвитанцияДата', 'КвитанцияВремя', 'КвитанцияСодержание', 'ПлательщикСчет',
               'ДатаСписано', 'Плательщик', 'ПлательщикИНН', 'Плательщик1', 'Плательщик2', 'Плательщик3',
               'Плательщик4', 'ПлательщикРасчСчет', 'ПлательщикБанк1', 'ПлательщикБанк2', 'ПлательщикБИК',
               'ПлательщикКорсчет', 'ПолучательСчет', 'ДатаПоступило', 'Получатель', 'ПолучательИНН', 'Получатель1',
               'Получатель2', 'Получатель3', 'Получатель4', 'ПолучательРасчСчет', 'ПолучательБанк1', 'ПолучательБанк2',
               'ПолучательБИК', 'ПолучательКорсчет', 'ВидПлатежа', 'ВидОплаты', 'Код', 'НазначениеПлатежа',
               'НазначениеПлатежа1', 'НазначениеПлатежа2', 'НазначениеПлатежа3', 'НазначениеПлатежа4',
               'НазначениеПлатежа5', 'НазначениеПлатежа6', 'СтатусСоставителя', 'ПлательщикКПП', 'ПолучательКПП',
               'ПоказательКБК', 'ОКАТО', 'ПоказательОснования', 'ПоказательПериода', 'ПоказательНомера',
               'ПоказательДаты', 'ПоказательТипа', 'Очередность', 'СрокАкцепта', 'ВидАккредитива', 'СрокПлатежа',
               'УсловиеОплаты1', 'УсловиеОплаты2', 'УсловиеОплаты3', 'ПлатежПоПредст', 'ДополнУсловия',
               'НомерСчетаПоставщика', 'ДатаОтсылкиДок']
    _mandatory_fields = ['Номер', 'Дата', 'Сумма', 'ПлательщикСчет', 'Плательщик', 'ПлательщикИНН', 'Плательщик1',
                         'ПлательщикРасчСчет', 'ПлательщикБанк1', 'ПлательщикБИК', 'ПлательщикКорсчет',
                         'ПолучательСчет', 'Получатель', 'ПолучательИНН', 'Получатель1', 'ПолучательРасчСчет',
                         'ПолучательБанк1', 'ПолучательБИК', 'ПолучательКорсчет', 'ВидОплаты', 'ВидПлатежа',
                         'СтатусСоставителя', 'ПлательщикКПП', 'ПолучательКПП', 'ПоказательКБК', 'ОКАТО',
                         'ПоказательОснования', 'ПоказательПериода', 'ПоказательНомера', 'ПоказательДаты']

    def __init__(self):
        BaseSection.__init__(self)

        for name in self._fields:
            self.__dict__[name] = None


class ClientBankExchange:
    """
    Файл обмена данными 1С
    """

    def __init__(self):
        self.__dict__['ОбщиеСведения'] = GeneralSection()
        self.__dict__['УсловияОтбора'] = FilterSection()
        self.__dict__['СекцияОстатков'] = BalancesSection()
        self.__dict__['СекцияПлатежногоДокумента'] = DocumentSection()

    def __str__(self):
        s = ""
        for item in ['ОбщиеСведения', 'УсловияОтбора', 'СекцияОстатков', 'СекцияПлатежногоДокумента']:
            s += "\n{}: \n{}".format(item, str(self.__dict__[item]))
        return s

    @property
    def document(self) -> str:
        """
        Свойство выдает полностью сформированный документ обмена данными клиент-банк-клиент в формате 1С.

        :return: Текст документа
        :rtype: str
        """
        s = "1CClientBankExchange\n{body}КонецФайла"
        body = self.__dict__['ОбщиеСведения'].document
        body += self.__dict__['УсловияОтбора'].document
        body += self.__dict__['СекцияОстатков'].document
        body += 'СекцияДокумент=Платежное поручение\n'
        body += self.__dict__['СекцияПлатежногоДокумента'].document
        body += 'КонецДокумента\n'
        return s.format(body=body)
