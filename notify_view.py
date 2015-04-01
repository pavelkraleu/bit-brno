from flask.views import View
from models import Ticket, PhoneSMS
from database import db_session


class Notify_view(View):
    def dispatch_request(self, payment_id):

        ticket = Ticket.query.filter(Ticket.payment_id == payment_id).first()

        if (ticket):
            if ticket.tariff == 20:
                message = "BRNO20"

            if ticket.tariff == 29:
                message = "BRNO"

            smska = PhoneSMS(phone=ticket.phone, message=message)

            smska.smstype = "send"

            smska.state = "waiting"

            smska.payment_id = ticket.payment_id

            db_session.add(smska)
            db_session.commit()

        return "aa"
