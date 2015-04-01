from flask.views import View
from flask import request
from models import Ticket, PhoneSMS, get_prepared_sms_for_ticket
import json
from database import db_session
from utils import parse_sms

from smssender import SmsSender


class Inbox_view(View):
    def dispatch_request(self):

        message = json.loads(request.args['message'])

        if message:
            smska = PhoneSMS(phone=message["from"], message=message["msg"])

            sms_data = parse_sms(message["msg"])

            smska.smstype = "recv"
            smska.state = "recv"

            waiting_ticket = self.get_waiting_ticket(sms_data)

            if waiting_ticket:
                waiting_ticket.valid_until = sms_data["valid_until"]
                waiting_ticket.valid_from = sms_data["valid_from"]
                waiting_ticket.price = sms_data["price"]
                waiting_ticket.code = sms_data["code"]

                ss = SmsSender()
                smsid = ss.sendSms(waiting_ticket.phone, get_prepared_sms_for_ticket(waiting_ticket))
                waiting_ticket.sms_sender_id = smsid

            db_session.add(smska)
            db_session.commit()

        # print(message)

        return "inbox_view"

    def get_waiting_ticket(self, sms_data):

        ticket = Ticket.query.filter(Ticket.status == "confirmed", Ticket.tariff == sms_data["price"],
                                     Ticket.code == None).order_by(Ticket.created_at.desc()).first()

        return ticket
