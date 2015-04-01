from flask.views import View
from flask import request
from models import Ticket, PhoneSMS
import json
from database import db_session


class Status_view(View):
    def dispatch_request(self, smsid):
        smska = PhoneSMS.query.filter(PhoneSMS.payment_id == smsid, PhoneSMS.state == "waiting").filter().first()

        if smska:
            print smska
            smska.state = "done"
            db_session.commit()

        return "status_view"
