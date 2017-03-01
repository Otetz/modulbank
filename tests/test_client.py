import json
import os

import pytest
import requests_mock

from modulbank import *


@pytest.fixture
def client():
    return ModulbankClient(token=os.environ['MODULBANK_TOKEN'], sandbox_mode=True)


def json_from_file(filename):
    with open('tests/data/' + filename) as json_file:
        return json.load(json_file)


def test_client():
    assert os.environ['MODULBANK_TOKEN']
    # noinspection PyShadowingNames
    client = ModulbankClient(token=os.environ['MODULBANK_TOKEN'])
    assert str(client) == "<ModulbankClient token='…' sandbox_mode='False' page_size=50>"


# noinspection PyShadowingNames
def test_accounts(client: ModulbankClient):
    with requests_mock.Mocker() as m:
        m.post("https://api.modulbank.ru/v1/account-info",
               json=json_from_file('accounts.json'),
               headers={'Content-Type': 'application/json; charset=utf-8'})
        res = client.accounts()
    assert isinstance(res, list)
    assert len(res) > 0
    assert isinstance(res[0], Company)
    assert res[0].name == 'ООО "Ромашка"'
    assert res[0].company_id == '70ca00f6-1f10-4964-aca6-a5ec032efe37'
    assert isinstance(res[0].bank_accounts, list)
    assert len(res[0].bank_accounts) > 0
    assert res[0].bank_accounts[0].name == 'Основной счет'
    assert res[0].bank_accounts[0].account_id == 'edb10116-5a93-4963-a53b-a5ec037177f0'
    assert res[0].bank_accounts[0].balance == Decimal(900000)
    assert res[0].bank_accounts[0].begin_date == datetime.date(2015, 10, 7)
    assert res[0].bank_accounts[0].category == AccountCategory.CheckingAccount
    assert res[0].bank_accounts[0].currency == Currency.RUR
    assert res[0].bank_accounts[0].number == '40802810070000000001'
    assert res[0].bank_accounts[0].status == AccountStatus.New
    assert isinstance(res[0].bank_accounts[0].bank, Bank)
    assert res[0].bank_accounts[0].bank.bic == '044525092'
    assert res[0].bank_accounts[0].bank.inn == '2204000595'
    assert res[0].bank_accounts[0].bank.kpp == '770443001'
    assert res[0].bank_accounts[0].bank.name == 'МОСКОВСКИЙ ФИЛИАЛ ОАО КБ"РЕГИОНАЛЬНЫЙ КРЕДИТ" Г.МОСКВА'
    assert res[0].bank_accounts[0].bank.corr_account == '30101810000000000001'


# noinspection PyShadowingNames
def test_balance(client: ModulbankClient):
    account_id = '58c20343-5d3b-422c-b98b-a5ec037df782'
    balance = "630170.0"
    with requests_mock.Mocker() as m:
        m.post(
            "https://api.modulbank.ru/v1/account-info/balance/{id}".format(id=account_id),
            text=balance, headers={'Content-Type': 'application/json; charset=utf-8'})
        res = client.balance(account_id)
    assert isinstance(res, Decimal)
    assert res == Decimal(balance)


# noinspection PyShadowingNames
def test_operation(client: ModulbankClient):
    account_id = '58c20343-5d3b-422c-b98b-a5ec037df782'
    with requests_mock.Mocker() as m:
        m.post("https://api.modulbank.ru/v1/operation-history/{id}".format(id=account_id),
               json=json_from_file('operations.json'),
               headers={'Content-Type': 'application/json; charset=utf-8'})
        res = client.operations(account_id)
    assert isinstance(res, list)
    assert len(res) > 0
    assert isinstance(res[0], Operation)
    assert res[0].status == OperationStatus.Received
    assert res[0].category == OperationCategory.Debet
    assert res[0].currency == Currency.RUR
    assert isinstance(res[0].amount, Decimal)
    assert res[0].amount == Decimal(100000)
    assert isinstance(res[0].amount_with_commission, Decimal)
    assert res[0].amount_with_commission == Decimal(100000)
    assert res[0].account_number == '30101810000000000001'
    assert isinstance(res[0].executed, datetime.datetime)
    assert isinstance(res[0].created, datetime.datetime)
    assert isinstance(res[0].contractor, Contractor)
    assert res[0].budgetary_and_tax is None


# noinspection PyShadowingNames
def test_operation_from(client: ModulbankClient):
    account_id = '58c20343-5d3b-422c-b98b-a5ec037df782'
    with requests_mock.Mocker() as m:
        m.post("https://api.modulbank.ru/v1/operation-history/{id}".format(id=account_id),
               json=json_from_file('operations_from.json'),
               headers={'Content-Type': 'application/json; charset=utf-8'})
        res = client.operations(account_id, SearchOptions(date_from=datetime.date(2016, 4, 1)))
    assert isinstance(res, list)
    assert len(res) > 0
    assert isinstance(res[0], Operation)


# noinspection PyShadowingNames
def test_operation_till(client: ModulbankClient):
    account_id = '58c20343-5d3b-422c-b98b-a5ec037df782'
    with requests_mock.Mocker() as m:
        m.post("https://api.modulbank.ru/v1/operation-history/{id}".format(id=account_id),
               json=json_from_file('operations_till.json'),
               headers={'Content-Type': 'application/json; charset=utf-8'})
        res = client.operations(account_id, SearchOptions(date_till=datetime.date(2016, 4, 1)))
    assert isinstance(res, list)
    assert len(res) > 0
    assert isinstance(res[0], Operation)


# noinspection PyShadowingNames
def test_operation_page():
    client = ModulbankClient(token=os.environ['MODULBANK_TOKEN'], sandbox_mode=True, page_size=10)
    account_id = '58c20343-5d3b-422c-b98b-a5ec037df782'
    with requests_mock.Mocker() as m:
        m.post("https://api.modulbank.ru/v1/operation-history/{id}".format(id=account_id),
               json=json_from_file('operations_page0.json'),
               headers={'Content-Type': 'application/json; charset=utf-8'})
        res = client.operations(account_id, SearchOptions(page=0))
        assert isinstance(res, list)
        assert len(res) == 10
        m.post("https://api.modulbank.ru/v1/operation-history/{id}".format(id=account_id),
               json=json_from_file('operations_page1.json'),
               headers={'Content-Type': 'application/json; charset=utf-8'})
        res = client.operations(account_id, SearchOptions(page=1))
        assert isinstance(res, list)
        assert len(res) == 5


# noinspection PyShadowingNames
def test_operation_wo_page(client: ModulbankClient):
    account_id = '58c20343-5d3b-422c-b98b-a5ec037df782'
    with requests_mock.Mocker() as m:
        m.post("https://api.modulbank.ru/v1/operation-history/{id}".format(id=account_id),
               json=json_from_file('operations_from.json'),
               headers={'Content-Type': 'application/json; charset=utf-8'})
        # noinspection PyTypeChecker
        res = client.operations(account_id, SearchOptions(page=None))
    assert isinstance(res, list)
    assert len(res) > 0
    assert isinstance(res[0], Operation)


# noinspection PyShadowingNames
def test_operation_category(client: ModulbankClient):
    account_id = '58c20343-5d3b-422c-b98b-a5ec037df782'
    with requests_mock.Mocker() as m:
        m.post("https://api.modulbank.ru/v1/operation-history/{id}".format(id=account_id),
               json=json_from_file('operations_category_debet.json'),
               headers={'Content-Type': 'application/json; charset=utf-8'})
        res = client.operations(account_id, SearchOptions(category=OperationCategory.Debet))
        assert isinstance(res, list)
        assert len(res) > 0
        m.post("https://api.modulbank.ru/v1/operation-history/{id}".format(id=account_id),
               json=json_from_file('operations_category_credit.json'),
               headers={'Content-Type': 'application/json; charset=utf-8'})
        res = client.operations(account_id, SearchOptions(category=OperationCategory.Credit))
        assert isinstance(res, list)
        assert len(res) == 0


# noinspection PyShadowingNames
def test_create_payment_draft(client):
    p = PaymentOrder(doc_num='994720', account_num='40802810670010011008', amount=Decimal(100.00), purpose='Для теста',
                     payer=Contractor(name='Индивидуальный предприниматель Александров Александр Александрович',
                                      inn='770400372208',
                                      bank=BankShort(account='40802810670010011008',
                                                     name='МОСКОВСКИЙ ФИЛИАЛ АО КБ \"МОДУЛЬБАНК\"',
                                                     bic='044525092', corr_acc='30101810645250000092')),
                     recipient=Contractor(name='МОСКОВСКИЙ ФИЛИАЛ АО КБ \"МОДУЛЬБАНК\"',
                                          inn='2204000595', kpp='771543001',
                                          bank=BankShort(account='30102810675250000092',
                                                         name='МОСКОВСКИЙ ФИЛИАЛ АО КБ \"МОДУЛЬБАНК\"',
                                                         bic='044525092', corr_acc='30102810675250000092')))
    with requests_mock.Mocker() as m:
        m.post("https://api.modulbank.ru/v1/operation-upload/1c",
               json=json_from_file('operation_upload.json'),
               headers={'Content-Type': 'application/json; charset=utf-8'})
        res = client.create_payment_draft(p)
    assert isinstance(res.errors, list)
    assert len(res.errors) == 0
    assert isinstance(res.total_loaded, int)
    assert res.total_loaded == 1
    assert isinstance(res.document, str)
    assert len(res.document) > 100


def test_company_str():
    data = json_from_file('accounts.json')
    c = Company(data[0])
    assert str(c).startswith('<Company ')


def test_bank_str():
    data = json_from_file('accounts.json')
    c = Bank(data[0]['bankAccounts'][0])
    assert str(c).startswith('<Bank ')


def test_bank_account_str():
    data = json_from_file('accounts.json')
    c = BankAccount(data[0]['bankAccounts'][0])
    assert str(c).startswith('<BankAccount ')


def test_bank_short_str():
    data = json_from_file('operations.json')
    c = Contractor(data[0])
    assert str(c.bank).startswith('<BankShort ')


def test_contractor_str():
    data = json_from_file('operations.json')
    c = Contractor(data[0])
    assert str(c).startswith('<Contractor ')


def test_operation_str():
    data = json_from_file('operations.json')
    c = Operation(data[0])
    assert str(c).startswith('<Operation ')


def test_client_bank_exchange_str():
    exchange = ClientBankExchange()
    assert str(exchange).startswith('\nОбщиеСведения')
    assert exchange.document.startswith('1CClientBankExchange')


# noinspection PyShadowingNames
def test_notify_request(client: ModulbankClient):
    data = json_from_file('new_operations.json')
    nr = NotifyRequest(data)
    assert nr.inn == '1111111111'
    assert nr.kpp == ''
    assert nr.check_signature(client.token)


def test_notify_request_str():
    data = json_from_file('new_operations.json')
    nr = NotifyRequest(data)
    assert str(nr).startswith('<NotifyRequest ')
