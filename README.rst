=========
modulbank
=========

.. image:: https://travis-ci.org/Otetz/modulbank.svg?branch=master
    :target: https://travis-ci.org/Otetz/modulbank
.. image:: https://readthedocs.org/projects/modulbank/badge/?version=latest
    :target: http://modulbank.readthedocs.io/ru/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://badge.fury.io/py/modulbank.svg
    :target: https://badge.fury.io/py/modulbank
.. image:: https://coveralls.io/repos/github/Otetz/modulbank/badge.svg?branch=master
    :target: https://coveralls.io/github/Otetz/modulbank?branch=master
.. image:: https://codeclimate.com/github/Otetz/modulbank/badges/gpa.svg
    :target: https://codeclimate.com/github/Otetz/modulbank
    :alt: Code Climate

Python client for ModulBank REST API

Installation
------------

Install modulbank package from PyPi::

  pip install modulbank

Getting started
---------------

Make sure to include this line in the beginning of your file::

  from modulbank import *

Set your API Token and choose sandbox mode or off::

  client = ModulbankClient(token=MODULBANK_TOKEN, sandbox_mode=True)

Make queries::

  print([str(acc) for acc in client.accounts()])
  print(client.balance('58c20343-5d3b-422c-b98b-a5ec037df782'))
  print([str(op) for op in client.operations('58c20343-5d3b-422c-b98b-a5ec037df782')])

Or send payment order::

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
  res = client.create_payment_draft(p)
  assert len(res.errors) == 0
  assert res.total_loaded == 1

Links
-----

- `Modulbank API <https://api.modulbank.ru/>`_