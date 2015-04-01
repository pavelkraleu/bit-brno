from flask.views import View
from flask import jsonify
from models import Ticket, PhoneSMS
from database import db_session


class New_view(View):
    def dispatch_request(self):
        smska = PhoneSMS.query.filter(PhoneSMS.state == "waiting").filter().first()

        messages = {}

        messages["messages"] = []

        if smska:
            message = {}

            message["id"] = smska.payment_id
            message["number"] = smska.phone
            message["txt"] = smska.message
            messages["messages"].append(message)

            smska.state = "sent"

        db_session.commit()

        return jsonify(messages)
