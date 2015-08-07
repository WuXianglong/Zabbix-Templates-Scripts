#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import smtplib
import requests
from email.mime.text import MIMEText

MAIL_HOST = "smtp.163.com"
MAIL_USER = "wuxianglong098@163.com"
MAIL_PWD = "password"


def send_mail(to_list, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = MAIL_USER
    msg['To'] = to_list
    try:
        s = smtplib.SMTP()
        s.connect(MAIL_HOST)
        s.login(MAIL_USER, MAIL_PWD)
        s.sendmail(MAIL_USER, to_list, msg.as_string())
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False


def send_email_by_mailgun(mail_to, subject, body):
    r = requests.post('https://api.mailgun.net/v2/colorba.us/messages', auth=('api', ''),
                      data={'from': '', 'to': ['%s' % mail_to], 'subject': '%s' % subject, 'text': '%s' % body})
    print r.text


if __name__ == '__main__':
    send_mail(*sys.argv[1: 4])

