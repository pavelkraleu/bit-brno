from datetime import datetime, timedelta
import os
import json
from flask import Flask, render_template, redirect, abort, request, session, url_for, jsonify
from urllib2 import Request, urlopen
from sqlalchemy import or_, and_, desc

from database import db_session, init_db
from models import Ticket, get_tariffs, PhoneSMS

from startup_view import Startup_view
from notify_view import Notify_view
from inbox_view import Inbox_view
from new_view import New_view
from status_view import Status_view

import settings
from smssender import SmsSender
from utils import getHash


app = Flask(__name__, static_folder='assets')
app.config['SECRET_KEY'] = settings.SECRET_KEY
PHONE_SESSION_KEY = 'phone'


# Sem se posle telefonni cislo z frontendu
app.add_url_rule('/startup', view_func=Startup_view.as_view('startup_view'), methods=["POST", "GET"])

# Tohle zavola platebni API
app.add_url_rule('/notify/<payment_id>', view_func=Notify_view.as_view('notify_view'), methods=["POST", "GET"])

# Sem se budou posilat prichozi SMSky
app.add_url_rule('/inbox', view_func=Inbox_view.as_view('inbox_view'), methods=["POST", "GET"])

# Tady si bude telefon tahat nove SMSky co ma odeslat
app.add_url_rule('/new', view_func=New_view.as_view('new_view'), methods=["POST", "GET"])

# Tedy bude telefon potvrzovat odeslatni zpravy
app.add_url_rule('/status/<smsid>', view_func=Status_view.as_view('status_view'), methods=["POST", "GET"])


@app.route("/")
def index():
    time_valid_until = datetime.now() - timedelta(hours=1)
    phone = session.get(PHONE_SESSION_KEY)

    tickets = []
    if phone is not None:
        tickets = Ticket.query.filter(Ticket.phone == phone)\
            .filter(or_(and_(Ticket.status == 'confirmed', Ticket.valid_until > time_valid_until), Ticket.status == 'received'))

    return render_template('index.html', phone=phone, tariffs=get_tariffs(), tickets=tickets)

@app.route("/initdb")
def initdb():
    init_db()
    return 'ok'


@app.route('/veselyadmin', methods=['POST','GET'])
def lastSentSms():
    ss = SmsSender()
    lastsmses = ss.getLastSsmses()
    return render_template('lastsentsms.html', lastsmses=lastsmses)

@app.route('/bitbrnoapi/getsmsstatus', methods=['POST','GET'])
def getSmsStatus():
    smsId = request.args.get('smsid')
    if smsId:
       ss = SmsSender()
       resp = ss.getSmsStatus(smsId)
       return jsonify({'status' : resp['status']})
    else:
       return 'no smsid'


@app.route("/ticket/buy/<tariff_id>", methods=['POST', 'GET'])
def ticket_buy(tariff_id):
    if request.method == 'POST' and int(tariff_id) in [20, 29]:
    # HOTFIX - umoznuje to volat i GETem
    # if int(tariff_id) in [20, 29]:
        phone = request.form['phone']

        ticket = Ticket(tariff=tariff_id, phone=phone)

        d = {}
        d["settled_currency"] = "CZK"
        d["return_url"] = "http://%s/notification" % request.host
        d["notify_url"] = "http://%s/notification" % request.host
        d["notify_email"] = "%s" % settings.bitcoinPayOwnerEmail
        d["price"] = tariff_id
        d["currency"] = "CZK"

        ref = {}
        ref["phone_number"] = phone
        ref["tariff"] = tariff_id
        d["reference"] = ref

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Token %s' % settings.bitcoinPayAuthToken
        }
        request_payment = Request('https://www.bitcoinpay.com/api/v1/payment/btc', data=json.dumps(d), headers=headers)

        response_body = urlopen(request_payment).read()

        data = json.loads(response_body)["data"]

        ticket.payment_id = data["payment_id"]
        ticket.status = data["status"]
        ticket.settled_amount = data["settled_amount"]
        ticket.settled_currency = data["settled_currency"]
        ticket.payment_response = json.dumps(data)

        db_session.add(ticket)
        db_session.commit()

        # ulozime payment id v session
        session["last_payment_id"] = ticket.payment_id
        # saving user's phone to be able to retrieve tickets overview
        session[PHONE_SESSION_KEY] = int(phone)

        return redirect(data["payment_url"], code=302)

    phone = session.get(PHONE_SESSION_KEY)
    tariff = get_tariffs(tariff_id)

    # return redirect(url_for('index'))
    return render_template('ticket_buy.html', tariff=tariff, phone=phone)


def process_notify(payment_id):
    ticket = Ticket.query.filter(Ticket.payment_id == payment_id).first()

    if(ticket):
        if ticket.tariff == 20:
            message = "BRNO20"

        if ticket.tariff == 29:
            message = "BRNO"

        smska = PhoneSMS(phone="90206", message=message)

        smska.smstype = "send"

        smska.state = "waiting"

        smska.payment_id = ticket.payment_id

        db_session.add(smska)
        db_session.commit()



@app.route("/notification", methods=['GET', 'POST'])
def process_notification():
    if request.method == 'POST':
        # only let it work with post that is valid based on given password
        if str(request.headers.get('BPSignature')) == getHash(request.data):
            jason = json.loads(request.data)
            
            if (jason.has_key("payment_id")):
                ticket = Ticket.query.filter(Ticket.payment_id == jason["payment_id"]).first()
                if ticket is not None:
                    ticket.status = jason["status"]
                    
                #tady zavolam neco co bude delat veci, kdyz bude potvrzena platba
                if jason["status"] == "confirmed":
                    payment_id = jason["payment_id"]
                    process_notify(payment_id)
                    # url = "http://10.0.0.143:5000/notify/"+payment_id
                    
                    # not_url = Request(url)
                    # response_body = urlopen(not_url).read()
                    
                    # uloz zmenu stavu ticketu
                    db_session.commit()
                    
            return 'ok'
        else:
            return 'data not validated using password'

    status = request.args.get('bitcoinpay-status')
    if status == 'cancel':
        payment_id = session.get("last_payment_id")
        print 'payment_id', payment_id
        if payment_id:
            ticket = Ticket.query.filter(Ticket.payment_id == payment_id).first()
            print 'ticket', ticket

            if ticket:
                ticket.status = 'cancelled'
                db_session.commit()
        return redirect(url_for('index'))

    return redirect('/ticket')

#ukazeme posledni listek co jsme vyrobili podle payment_id, je li relevantni
@app.route("/ticket")
def ticket_detail_session():
    if "last_payment_id" in session:
        ticket = Ticket.query.filter(Ticket.payment_id == session["last_payment_id"]).first()
        if (ticket is None) or (ticket.status not in  ["pending", "received", "confirmed"]):
            abort(404)

        return render_template('ticket_detail.html', ticket=ticket)
    else:
        abort(404)
    return 'ok'

@app.route("/ticket/<ticket_id>")
def ticket_detail(ticket_id):
    ticket = Ticket.query.filter(Ticket.id == ticket_id).first()
    if ticket is None:
        abort(404)

    return render_template('ticket_detail.html', ticket=ticket)

@app.route("/bitbrnoapi/ticket-<ticket_id>")
def ticket_detail_api(ticket_id):
    ticket = Ticket.query.filter(Ticket.id == ticket_id).first()
    if ticket is None:
        abort(404)

    return jsonify({'valid' : ticket.is_valid})

@app.route('/bitbrnoapi/sendsms', methods=['POST','GET'])
def bbSendSms():
    ss = SmsSender()
    if request.args.get('n'):
      ss.sendSms(request.args.get('n'), request.args.get('m','nic'))
    return 'ok'

@app.route('/bitbrnoapi/delivery', methods=['POST','GET'])
def bbSmsDelivery():
    ss = SmsSender()
    ss.saveDeliveryStatus(request.args)
    return 'ok'

"""
@app.route('/ticket/update_statuses')
def update_ticket_statuses():
   for ticket in Ticket.query.filter(or_(Ticket.status == "pending", Ticket.status == "received")).all():
       headers = {
         'Content-Type': 'application/json',
         'Authorization': 'Token %s' % settings.bitcoinPayAuthToken
       }
       request_status = Request('https://www.bitcoinpay.com/api/v1/payment/btc/'+str(ticket.status), headers=headers)

       response_body = urlopen(request_status).read()

       data = json.loads(response_body)["data"]

       ticket.status = data["status"]

       db_session.commit()
   return 'ok'
"""

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


port = os.getenv('VCAP_APP_PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port), debug=True)
