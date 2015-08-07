#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time
import shutil
import MySQLdb
import smtplib
import requests
import datetime

from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart


# based on zabbix 2.4.4
ZABBIX_HOST = '127.0.0.1'
ZABBIX_USER = 'Admin'
ZABBIX_PWD = 'password'

ZABBIX_DB_HOST = 'localhost'
ZABBIX_DB_USER = 'zabbix'
ZABBIX_DB_PWD = 'db_password'
ZABBIX_DB_NAME = 'zabbix'

GRAPH_PATH = '/tmp/zabbix_graph'
GRAPH_PERIOD = 86400  # one day

EMAIL_DOMAIN = '163.com'
EMAIL_USERNAME = 'wuxianglong098'
EMAIL_PASSWORD = 'email_password'


def query_screens(screen_name):
    conn = MySQLdb.connect(host=ZABBIX_DB_HOST, user=ZABBIX_DB_USER, passwd=ZABBIX_DB_PWD,
                           db=ZABBIX_DB_NAME, charset='utf8', connect_timeout=20)
    cur = conn.cursor()
    count = cur.execute("""
            select a.name, a.screenid, b.resourceid, b.width, b.height
                from screens a, screens_items as b
                where a.screenid=b.screenid and a.templateid<=>NULL and a.name='%s'
                order by a.screenid;
            """ % screen_name)
    if count == 0:
        result = 0
    else:
        result = cur.fetchall()

    cur.close()
    conn.close()

    return result


def generate_graphs(screens):
    login_resp = requests.post('http://%s/index.php' % ZABBIX_HOST, data={
        'name': ZABBIX_USER,
        'password': ZABBIX_PWD,
        'enter': 'Sign in',
        'autologin': 1,
    })
    session_id = login_resp.cookies['zbx_sessionid']

    graphs = []
    for i, (screen_name, screen_id, graph_id, width, height) in enumerate(screens):
        params = {
            'screenid': screen_id,
            'graphid': graph_id,
            'width': width * 2,
            'height': height * 2,
            'period': GRAPH_PERIOD,
            'stime': datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S'),
        }
        resp = requests.get('http://%s/chart2.php' % ZABBIX_HOST, params=params,
                            cookies={'zbx_sessionid': session_id})
        file_name = '_'.join(map(str, screens[i][:3])).replace(' ', '_') + '.png'
        with open(os.path.join(GRAPH_PATH, file_name), 'wb') as fp:
            fp.write(resp.content)
        graphs.append(file_name)

    return graphs


def send_mail(screen_name, graphs, to_list):
    me = 'Zabbix <%s@%s>' % (EMAIL_USERNAME, EMAIL_DOMAIN)

    def _create_msg():
        msg = MIMEMultipart('related')
        msg['Subject'] = 'Zabbix Screen Report: %s' % screen_name
        msg['From'] = me
        msg['To'] = ';'.join(to_list)
        msg.preamble = 'This is a multi-part message in MIME format.'

        contents = "<h1>Screen %s</h1><br>" % screen_name
        contents += "<table>"
        for g_name in graphs:
            with open(os.path.join(GRAPH_PATH, g_name), 'rb') as fp:
                msg_image = MIMEImage(fp.read())
                msg_image.add_header('Content-ID', "<%s>" % g_name)
                msg.attach(msg_image)

            contents += ''
            contents += "<tr><td><img src='cid:%s'></td></tr>" % g_name
        contents += "</table>"

        msg_text = MIMEText(contents, 'html')
        msg_alternative = MIMEMultipart('alternative')
        msg_alternative.attach(msg_text)
        msg.attach(msg_alternative)

        return msg

    try:
        server = smtplib.SMTP()
        server.connect('smtp.%s' % EMAIL_DOMAIN)
        server.login('%s@%s' % (EMAIL_USERNAME, EMAIL_DOMAIN), EMAIL_PASSWORD)
        server.sendmail(me, to_list, _create_msg().as_string())
        server.close()
        print 'send mail Ok!'
    except Exception, e:
        print e


if __name__ == '__main__':
    # remove old dirs
    if os.path.exists(GRAPH_PATH):
        shutil.rmtree(GRAPH_PATH)
    os.makedirs(GRAPH_PATH)

    for srn_name in (u'Zabbix server', u'Nginx Connections'):
        # get screens
        all_screens = query_screens(srn_name)
        print all_screens

        # generate graphs
        graphs = generate_graphs(all_screens)

        send_mail(srn_name, graphs, ['wuxianglong098@163.com'])
