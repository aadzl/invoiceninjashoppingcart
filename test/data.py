import json
from collections import namedtuple

countries = [dict(name='Spain', id=1)]

frequencies = [{u'id': 1, u'name': u'Weekly'}, {u'id': 2, u'name': u'Two weeks'},
               {u'id': 3, u'name': u'Four weeks'}, {u'id': 4, u'name': u'Monthly'},
               {u'id': 5, u'name': u'Three months'},
               {u'id': 6, u'name': u'Six months'}, {u'id': 7, u'name': u'Annually'}]

static = dict(industries=None, currencies=None, sizes=None,
              fonts=None, timezones=None, invoiceStatus=None,
              countries=countries, languages=None, paymentTypes=None,
              paymentTerms=None, gateways=None, frequencies=frequencies,
              banks=None, invoiceDesigns=None, datetimeFormats=None,
              dateFormats=None)

FakeRequest = namedtuple('FakeRequest', ['json', 'status_code', 'headers'])

mimetype = {'content-type': 'application/json'}

def return_json():
    return dict(data=static)

static_response = FakeRequest(return_json, 200, mimetype)