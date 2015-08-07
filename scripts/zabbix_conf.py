#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import time
import requests

HOSTS = [
    ['host-name', 'public-ip', 'private-ip'],
]

DOMAIN = "http://127.0.0.1/api_jsonrpc.php"
JSON_HEADERS = {"content-type": "application/json"}
GROUP_ID = 2
TEMPLATE_ID = 10001


def get_list(filename):
    lst = []
    with open(filename, 'r') as f:
        for i in f.readlines():
            lst.append(i.rstrip())
    return lst


def get_token():
    login_data = json.dumps({
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": "Admin",
            "password": "password",
        },
        "id": 1
    })
    request = requests.post(DOMAIN, data=login_data, headers=JSON_HEADERS, timeout=30)

    print request.text

    return request.json()['result']


def add_host(host):
    data = json.dumps({
        "jsonrpc": "2.0",
        "method": "host.create",
        "params": {
            "host": "%s" % host[0],
            "interfaces": [
                {
                    "type": 1,
                    "main": 1,
                    "useip": 1,
                    "ip": host[2],
                    "dns": "",
                    "port": "10050"
                }
            ],
            "groups": [{
                "groupid": GROUP_ID,
            }],
            "templates": [{
                "templateid": TEMPLATE_ID,
            }],
        },
        "auth": get_token(),
        "id": 1,
    })
    request = requests.post(DOMAIN, data=data, headers=JSON_HEADERS)
    print data
    print request.json()


if __name__ == "__main__":
    for ht in HOSTS:
        print ht
        add_host(ht)
