from datetime import datetime
import json
import re
from urllib2 import urlopen, Request


SMS_PATTERN = re.compile(
    r'^.+(?: (?P<price>[0-9]{1,3}) Kc)\..+'  # price
    r'Platnost: Od:? (?P<valid_from>[0-9\.]{6,8} [0-9:]{4,5})'  # time from
    r' Do:? (?P<valid_until>[0-9\.]{6,8} [0-9:]{4,5}).?'  # time to
    r' (?P<code1>[A-Za-z0-9]{9})[ /]{1,3}(?P<code2>[0-9]{6}).*$',  # codes
    re.IGNORECASE
)
datetime_format = "%d.%m.%y %H:%M"


def parse_sms(sms_content):

    res = SMS_PATTERN.search(sms_content)

    if res is None:
        return None

    code1 = res.group('code1')
    code2 = res.group('code2')
    code = "%s/%s" % (code1, code2)

    return {
        'price': int(res.group('price')),
        'valid_from': datetime.strptime(res.group('valid_from'), datetime_format),
        'valid_until': datetime.strptime(res.group('valid_until'), datetime_format),
        'code': code,
    }


def get_mbtc_for(amount, currency='CZK'):
    """
    vrati kolik milibitcoinu dostanu za nejaky pocet penez

    """
    status_request = Request('https://www.bitcoinpay.com/api/v1/rates/btc')
    response_body = urlopen(status_request).read()

    rates = json.loads(response_body)

    bitcoina = 0
    for rate in rates:
        if currency in rate:
            bitcoina = float(rate[currency])
            break

    try:
        return round((float(amount) / bitcoina) * 1000, 3)
    except ZeroDivisionError:
        return None

