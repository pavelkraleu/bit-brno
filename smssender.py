# -*- coding: UTF-8 -*-

import urllib, hashlib, string, random
from datetime import datetime, date, time
from time import gmtime, strftime
from lxml import etree
import MySQLdb
import settings

class SmsSender():
  def __init__(self):
    self.serviceUrl = settings.smssenderServiceUrl
    self.login = settings.smssenderLogin
    self.password = settings.smssenderPassword
    self.answerMail = settings.smssenderAnswerMail
    self.connectDB()

  def connectDB(self):
    self.conn = MySQLdb.connect (
        host = settings.smssenderDBHost,
        user = settings.smssenderDBUser,
        passwd = settings.smssenderDBPasswd,
        db = settings.smssenderDBDb,
        charset='utf8')

    self.cursor = self.conn.cursor()
    self.cursor.execute('SET NAMES utf8;')
    self.cursor.execute('SET CHARACTER SET utf8;')
    self.cursor.execute('SET character_set_connection=utf8;')

  def query(self,query, args=(), one=False):
      self.debugSqlArgs = args
      self.debugSqlQuery = query
      self.cursor.execute(query,args)
      self.conn.commit()

      rv = [dict((self.cursor.description[idx][0], value)
              for idx, value in enumerate(row)) for row in self.cursor.fetchall()]
      return (rv[0] if rv else None) if one else rv

  def randomString(self,size):
    chars=string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

  def logSent(self,smsId,price, number, message):
    self.query("INSERT INTO smssender (`id`,`price`, `phonenumber`, `text`) VALUES (%s,%s,%s,%s) ", (smsId,price, number, message))

  def sendRequest(self,url, fake=False):
    if fake:
      textResponse = """<?xml version='1.0' encoding='utf-8'?>
      <result>
      <err>0</err>
      <price>%f</price>
      <sms_count>1</sms_count>
      <credit>720.46</credit>
      <sms_id>14535048</sms_id>
      </result>
    """ % float(int(random.randint(4,8)) / float(10))
    else:
      handler = urllib.urlopen(url)
      textResponse = handler.read()
    tree = etree.fromstring(textResponse)
    result = {}
    for child in tree:
      result[child.tag] = child.text
    return result

  def sendSms(self,number,message):
    timeCode = strftime("%Y%m%dT%H%M%S")
    sul = self.randomString(5)
    auth = hashlib.md5('%s%s%s' % (self.password,timeCode,sul)).hexdigest()
    url = "%s&login=%s&time=%s&auth=%s&sul=%s&number=%s&message=%s&action=send_sms&answer_mail=%s" % \
          (self.serviceUrl, self.login, timeCode,auth, sul,number,message, self.answerMail)
    result = self.sendRequest(url)

    if result.get('price') and result.get('sms_id') and number and message:
      self.logSent(result['sms_id'],result['price'], number, message)
      return result['sms_id']
    else:
      return None

  def saveDeliveryStatus(self,req):
    if not req.get('type') == 'delivery_report':
      return None
    statusTable = {
      '0' : 'sentconfirmed', '1' : 'delivered', '2' : 'saved', '3' : 'notdelivered', '5' : 'expired'
    }
    status = statusTable[req.get('status')]
    self.query("""
      UPDATE smssender SET `status` = %s, `updated`=NOW()
      WHERE `id` = %s
    """, (status,req.get('sms_id')))

  def getSmsStatus(self, smsId):
     return self.query("SELECT * FROM smssender WHERE `id` = %s", [smsId], one=True)

  def getLastSsmses(self):
     return self.query("""
      SELECT t.id ticketid, t.phone ticketphone , t.status ticketstatus, s.status sendstatus, t.created_at ticketcreated
      FROM tickets t
      LEFT JOIN smssender s ON t.sms_sender_id = s.id
      ORDER BY t.created_at DESC LIMIT 30
     """)

