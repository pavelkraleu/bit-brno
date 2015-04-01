from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from database import Base

from utils import get_mbtc_for

from smssender import SmsSender


def get_tariffs(tariff_id=None):
    tariffs = [
        {'id': 20, 'price': 20, 'mbtc': get_mbtc_for(20, 'CZK'), 'time': 20, 'enabled': False},
        {'id': 29, 'price': 29, 'mbtc': get_mbtc_for(29, 'CZK'), 'time': 75, 'enabled': False},
    ]

    if tariff_id is not None:
        for t in tariffs:
            if t['id'] == int(tariff_id):
                return t

    return tariffs

def get_prepared_sms_for_ticket( ticket):
    return get_prepared_sms(ticket.phone, ticket.tariff, ticket.valid_from, ticket.valid_until, ticket.code)

def get_prepared_sms(self, number, tariff, valid_from, valid_until, code):
    return "Souhrn z jizdenky pro cislo "+number+"; DPMB,a.s. Jizdenka prestupni "+tariff+" Kc. Platnost: od "+valid_from.strftime("%H:%M %d. %m. %Y")+" do "+valid_until.strftime("%H:%M %d. %m. %Y")+" "+code

def get_number( payment_id):
    sms = PhoneSMS.query.filter(PhoneSMS.payment_id == payment_id).first()
    if sms is not None:
        return sms.phone

    return 0

class Ticket(Base):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True)
    tariff = Column(Integer)
    phone = Column(Integer)
    created_at = Column(DateTime)
    payment_id = Column(String(50))
    status = Column(String(512))
    settled_amount = Column(Float)
    settled_currency = Column(String(3))
    payment_response = Column(String(1024))
    sms_sender_id = Column(Integer) #orwenovo odesilani
    phone_sender_id = Column(Integer) #pavlovo odesilani

    # Detaily sms jizdenky
    valid_until = Column(DateTime)
    valid_from = Column(DateTime)
    price = Column(Integer)
    code = Column(String(512))

    def __init__(self, tariff, phone):
        self.tariff = tariff
        self.phone = phone
        self.created_at = datetime.now()

    def __repr__(self):
        return '<Ticket [tariff: %r] [phone: %s]>' % (self.id or 'new', self.phone)

    @property
    def duration(self):
        return {20: 20, 29: 75}[self.tariff]

    @property
    def is_visible(self):
        return self.status in ['received', 'confirmed']

    @property
    def is_confirmed(self):
        return self.status == 'confirmed' and self.code is not None


    @property
    def is_valid(self):
        return self.is_confirmed and self.valid_until >= datetime.now()


class PhoneSMS(Base):
    __tablename__ = 'phonesms'  
    
    id = Column(Integer, primary_key=True)  
    created_at = Column(DateTime)

    phone = Column(String(20))

    message = Column(String(2048))

    smstype = Column(String(7))

    state = Column(String(30))

    payment_id = Column(String(50))

    def __init__(self, phone, message):
        self.phone = phone
        self.message = message
        self.created_at = datetime.now()

    def __repr__(self):
        return "Phone : {} ID: {}".format(self.phone,self.id)

