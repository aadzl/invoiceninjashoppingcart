# -*- coding: utf8 -*-
#
# Copyright (C) 2016 Scifabric LTD.
#
# PyBossa is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyBossa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

from flask import Flask, jsonify, request
from forms import NewClient, NewInvoice, INVOICE_SCHEMA, INVOICE_ITEMS_SCHEMA
from flask_cors import CORS
from flask_wtf.csrf import generate_csrf, CsrfProtect
from invoiceninja import invoiceNinja
from jsonschema import validate, Draft4Validator


app = Flask(__name__)
app.config.from_object('settings')
cors = CORS(app, resources={r"/*": {"origins": app.config.get('CORS'), "supports_credentials": True}})
invoiceninja = invoiceNinja(app.config.get('TOKEN'))
CsrfProtect(app)


@app.route("/newclient", methods=['GET', 'POST'])
def newclient():
    """Endpoint for creating a new client."""
    form = NewClient()
    if request.method == 'GET':
        resp = form.data
        resp['csrf_token'] = generate_csrf()
        return jsonify(resp)
    else:
        if form.validate_on_submit():
            client = format_client_data(form.data)
            res = invoiceninja.create_client(client)
            return jsonify(res)
        else:
            return jsonify(form.errors)


@app.route("/newinvoice", methods=['GET', 'POST'])
def newinvoice():
    """Endpoint for creating a new invoice."""
    form = NewInvoice()
    if request.method == 'GET':
        resp = form.data
        resp['csrf_token'] = generate_csrf()
        return jsonify(resp)
    else:
        invoice = request.get_json()
        invoice = format_invoice_data(invoice)
        if (not invoice.get('message') and not invoice.get('cause')):
            if (invoice.get('recurring') is not None and
                    invoice.get('recurring') != ''):
                if invoice.get('email_invoice'):
                    del invoice['email_invoice']
                res = invoiceninja.create_recurring_invoice(invoice)
            else:
                res = invoiceninja.create_invoice(invoice)
            return jsonify(res)
        error = dict(message=invoice['message'])
        return jsonify(error)


@app.route("/countries")
def get_countries():
    """Return a list of countries and its IDs."""
    return jsonify(invoiceninja.static['countries'])


def format_invoice_data(invoice):
    keys = ['csrf_token', 'qty', 'cost']
    invoice_validator = Draft4Validator(INVOICE_SCHEMA)
    invoice_items_validator = Draft4Validator(INVOICE_ITEMS_SCHEMA)
    for k in keys:
        if invoice.get(k):
            del invoice[k]
    if invoice_validator.is_valid(invoice):
        for item in invoice.get('invoice_items'):
            if not invoice_items_validator.is_valid(item):
                errors = sorted(invoice_items_validator.iter_errors(item),
                                key=lambda e: e.path)
                return errors[0].__dict__
        return invoice
    else:
        errors = sorted(invoice_validator.iter_errors(invoice),
                        key=lambda e: e.path)
        return errors[0].__dict__


def format_client_data(data):
    client = dict()
    client['contact'] = dict()
    client['contact'] = {'email': data['email'], 'first_name': data['first_name'],
                         'last_name': data['last_name']}
    if not data['name']:
        data['name'] = "%s %s" % (data['first_name'], data['last_name'])
    del data['email']
    del data['first_name']
    del data['last_name']
    client.update(data)
    return client


if __name__ == "__main__":  # pragma: no cover
    app.run()
