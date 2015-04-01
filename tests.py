from datetime import datetime
from utils import parse_sms


TEXTS = (
    (
        "DPMB,a.s. Jizdenka prestupni 20 Kc.Plati v zonach 100+101. Linky 1-99 mimo vlak.Platnost: od 12.2.15 19:54 do 12.2.15 20:14. MRhxyCjRt/110822",
        {
            'price': 20,
            'valid_from': datetime(2015, 2, 12, 19, 54, 0),
            'valid_until': datetime(2015, 2, 12, 20, 14, 0),
            'code': 'MRhxyCjRt/110822',
        }
    ),
    (
        "DPMB, a.s. Jizdenka prestupni 20 Kc. Plati v zonach 100+101 mimo vlak.Platnost: Od: 28.3.15 7:49 Do: 28.3.15 8:09 2PuUrMs7F / 207592",
        {
            'price': 20,
            'valid_from': datetime(2015, 3, 28, 7, 49, 0),
            'valid_until': datetime(2015, 3, 28, 8, 9, 0),
            'code': '2PuUrMs7F/207592',
        }
    ),
    (
        "DPMB, a.s. Jizdenka prestupni 29 Kc. Plati v zonach 100+101 mimo vlak. Platnost: Od: 28.3.15 7:49 Do: 28.3.15 9:04 hWMEEtZ2S / 358615",
        {
            'price': 29,
            'valid_from': datetime(2015, 3, 28, 7, 49, 0),
            'valid_until': datetime(2015, 3, 28, 9, 4, 0),
            'code': 'hWMEEtZ2S/358615',
        }
    ),
    (
        "DPMB, a.s. Jizdenka prestupni 154 Kc. Plati v zonach 100+101 mimo vlak. Platnost: Od: 1.1.15 1:01 Do: 1.1.15 1:02 hWMEEtZ2S / 358615",
        {
            'price': 154,
            'valid_from': datetime(2015, 1, 1, 1, 1, 0),
            'valid_until': datetime(2015, 1, 1, 1, 2, 0),
            'code': 'hWMEEtZ2S/358615',
        }
    ),
    (
        "DPMB, a.s. Jizdenka prestupni 29 Kc. Plati v zonach 100+101 mimo vlak. Platnost: Od: 28.3.15 7:49",
        None
    ),
    (
        "",
        None
    )
)


def test_parse_sms():
    for text, res in TEXTS:
        assert parse_sms(text) == res
