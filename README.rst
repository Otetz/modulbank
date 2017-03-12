=========
modulbank
=========

.. image:: https://travis-ci.org/Otetz/modulbank.svg?branch=master
    :target: https://travis-ci.org/Otetz/modulbank
.. image:: https://readthedocs.org/projects/modulbank/badge/?version=latest
    :target: http://modulbank.readthedocs.io/en/latest/?badge=latest
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

Install modulbank package from `PyPI <https://pypi.python.org/pypi>`_
::

  pip install modulbank

Getting started
---------------

Make sure to include this lines in the beginning of your code::

  from modulbank.client import ModulbankClient
  import modulbank.structs as structs

Set your *API Token* and choose *sandbox mode* ``on`` or ``off``::

  client = ModulbankClient(token=MODULBANK_TOKEN, sandbox_mode=True)

Make queries::

  print([str(acc) for acc in client.accounts()])
  print(client.balance('58c20343-5d3b-422c-b98b-a5ec037df782'))
  print([str(op) for op in client.operations('58c20343-5d3b-422c-b98b-a5ec037df782')])

Or send payment order::

  p = structs.PaymentOrder(
      doc_num='994720', account_num='40802810670010011008', amount=Decimal(100.00), purpose='Для теста',
      payer=structs.Contractor(name='Индивидуальный предприниматель Александров Александр Александрович',
                               inn='770400372208', kpp='',
                               bank=structs.BankShort(account='40802810670010011008',
                                                      name='МОСКОВСКИЙ ФИЛИАЛ АО КБ "МОДУЛЬБАНК"',
                                                      bic='044525092', corr_acc='30101810645250000092')),
      recipient=structs.Contractor(name='МОСКОВСКИЙ ФИЛИАЛ АО КБ "МОДУЛЬБАНК"',
                                   inn='2204000595', kpp='771543001',
                                   bank=structs.BankShort(account='30102810675250000092',
                                                          name='МОСКОВСКИЙ ФИЛИАЛ АО КБ "МОДУЛЬБАНК"',
                                                          bic='044525092', corr_acc='30102810675250000092')))
  res = client.create_payment_draft(p)
  assert len(res.errors) == 0
  assert res.total_loaded == 1

Helper class for processing web-hooks
-------------------------------------

Sample usage of class ``NotifyRequest``::

  @app.route('/modulbank', methods=['POST'])
  def notify():
    client = ModulbankClient(token=MODULBANK_TOKEN)

    if not request.is_json:
        return make_response(render_template('template.json'), 400)

    nr = structs.NotifyRequest(request.json)

    # Filter only needed company's operations
    if nr.inn != INN or nr.kpp != KPP:
        return make_response(render_template('template.json'), 200)

    # Check signature in `SHA1Hash` field
    if not nr.check_signature(MODULBANK_TOKEN):
        return make_response(render_template('template.json'), 403)

    #
    # Make something with `nr`
    #

    make_response(render_template('template.json'), 200)

TODO
----

- OAuth 2 authorization.

Links
-----

- `Modulbank API <https://api.modulbank.ru/>`_