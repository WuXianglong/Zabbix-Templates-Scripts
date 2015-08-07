#!/usr/bin/python
#-*- coding: utf-8 -*-
import os
import json

ports = [line.split()[3].split(':')[1] for line in os.popen('netstat -tpln | grep LISTEN | grep -v tcp6').readlines()]
data = {
    'data': [{'{#TCP_PORT}': p} for p in set(ports)],
}
print json.dumps(data, sort_keys=True, indent=4)

