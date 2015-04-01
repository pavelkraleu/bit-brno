import os


SECRET_KEY = os.environ.get('APP_SECRET_KEY')

DATABASE = {
    'NAME': os.environ.get('DB_NAME'),
    'HOST': os.environ.get('DB_HOST'),
    'PORT': os.environ.get('DB_PORT'),
    'USER': os.environ.get('DB_USER'),
    'PASS': os.environ.get('DB_PASS')
}

bitcoinPayOwnerEmail = os.environ.get('BITCOIN_PAY_OWNER_ACCOUNT_EMAIL')
bitcoinPayAuthToken = os.environ.get('BITCOIN_PAY_AUTH_TOKEN')

smssenderAnswerMail = os.environ.get('SMSSENDER_ANSWER_MAIL')
smssenderServiceUrl = os.environ.get('SMSSENDER_SERVICE_URL')
smssenderLogin = os.environ.get('SMSSENDER_LOGIN')
smssenderPassword = os.environ.get('SMSSENDER_PASSWORD')

smssenderDBHost = DATABASE['HOST']
smssenderDBUser = DATABASE['USER']
smssenderDBPasswd = DATABASE['PASS']
smssenderDBDb = DATABASE['NAME']


try:
    from local_settings import *
except ImportError:
    pass
