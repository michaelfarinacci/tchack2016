from flask import Flask, redirect, url_for, render_template, request, flash

import flask
import os
from os.path import join, dirname
from dotenv import load_dotenv
import braintree
import json

app = Flask(__name__)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
app.secret_key = os.environ.get('APP_SECRET_KEY')

braintree.Configuration.configure(
    os.environ.get('BT_ENVIRONMENT'),
    os.environ.get('BT_MERCHANT_ID'),
    os.environ.get('BT_PUBLIC_KEY'),
    os.environ.get('BT_PRIVATE_KEY')
)

TRANSACTION_SUCCESS_STATUSES = [
    braintree.Transaction.Status.Authorized,
    braintree.Transaction.Status.Authorizing,
    braintree.Transaction.Status.Settled,
    braintree.Transaction.Status.SettlementConfirmed,
    braintree.Transaction.Status.SettlementPending,
    braintree.Transaction.Status.Settling,
    braintree.Transaction.Status.SubmittedForSettlement
]

orders = {'45321': {'total': 100, 'tax': 5}}

@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('new_checkout'))

@app.route('/checkouts/new', methods=['GET'])
def new_checkout():
    return render_template('checkouts/new.html', client_token=client_token)

@app.route('/create_order', methods=['GET'])
def create_order():
    total = flask.request.args['total']
    items = flask.request.args['items']
    tax = flask.request.args['tax']
    merchant_id = flask.request.args['merchantId']
    order_id = 45321
    return order_id

@app.route('/get_order', methods=['GET'])
def get_order():
    order_id = flask.request.args['orderId']
    order_data = orders[order_id]
    json_order_data = json.dumps(order_data)
    resp = flask.Response(response=json_order_data, status=200, mimetype="application/json")
    return resp

@app.route('/customer', methods=['GET'])
def customer():
    return render_template('customer.html')

@app.route('/merchant', methods=['GET'])
def merchant():
    return render_template('merchant.html')

@app.route('/checkouts/<transaction_id>', methods=['GET'])
def show_checkout(transaction_id):
    transaction = braintree.Transaction.find(transaction_id)
    result = {}
    if transaction.status in TRANSACTION_SUCCESS_STATUSES:
        result = {
            'header': 'Sweet Success!',
            'icon': 'success',
            'message': 'Your test transaction has been successfully processed. See the Braintree API response and try again.'
        }
    else:
        result = {
            'header': 'Transaction Failed',
            'icon': 'fail',
            'message': 'Your test transaction has a status of ' + transaction.status + '. See the Braintree API response and try again.'
        }

    return render_template('checkouts/show.html', transaction=transaction, result=result)

@app.route('/checkouts', methods=['POST'])
def create_checkout():
    result = braintree.Transaction.sale({
        'amount': request.form['amount'],
        'payment_method_nonce': request.form['payment_method_nonce'],
    })

    if result.is_success or result.transaction:
        return redirect(url_for('show_checkout',transaction_id=result.transaction.id))
    else:
        for x in result.errors.deep_errors: flash('Error: %s: %s' % (x.code, x.message))
        return redirect(url_for('new_checkout'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4567, debug=True)
