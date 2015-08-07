#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import Queue
import socket
import paramiko
import threading

QUEUE = Queue.Queue()
SSH_USERNAME = 'ubuntu'
SSH_KEY = '/home/xianglong/.ssh/admin.pem'

HOSTS = [
    ['host-name', 'public-ip', 'private-ip'],
]
THREAD_NUM = 10
ZABBIX_SERVER = '127.0.0.1'


def get_list(filename):
    lst = []
    with open(filename, 'r') as f:
        for i in f.readlines():
            lst.append(i.rstrip().split())
    return lst


class SSH(paramiko.SSHClient):

    def call(self, command, bufsize=-1):
        new_exec = self._transport.open_session()
        new_exec.exec_command(command)

        stdin = new_exec.makefile('wb', bufsize)
        stdout = new_exec.makefile('rb', bufsize)
        stderr = new_exec.makefile('rb', bufsize)
        status = new_exec.recv_exit_status()

        return stdin, stdout, stderr, status


def connect(ip):
    """ connect server via ssh protocol """
    session = SSH()
    session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    rsa_key = paramiko.RSAKey.from_private_key_file(SSH_KEY)

    try:
        session.connect(ip, 22, username=SSH_USERNAME, pkey=rsa_key, timeout=15)
    except socket.timeout:
        print '%s connect timeout' % ip
        return None

    return session


def general_task(name):
    tasks = [
        [1, 'sudo mv /etc/zabbix/zabbix_agentd.conf /tmp/'],
        [1, 'sudo service zabbix-agent stop'],
        [2, 'sudo apt-get purge zabbix_agent -y'],
        [2, 'sudo killall zabbix_agentd'],
        [3, 'sudo mv /usr/local/zabbix /tmp/zabbix_%s' % time.time()],
        [3, 'sudo userdel zabbix'],
        [3, 'rm zabbix_agents_2.4.4.linux2_6.amd64.tar.gz'],
        [4, 'sudo wget http://www.zabbix.com/downloads/2.4.4/zabbix_agents_2.4.4.linux2_6.amd64.tar.gz'],
        [3, 'sudo mkdir /usr/local/zabbix'],
        [5, 'sudo tar -zxvf zabbix_agents_2.4.4.linux2_6.amd64.tar.gz -C /usr/local/zabbix'],
        [6, 'sudo chown -R root:root /usr/local/zabbix'],
        [7, "sudo sed -i -e 's/ServerActive=127.0.0.1/ServerActive=%s/g' /usr/local/zabbix/conf/zabbix_agentd.conf"
         % ZABBIX_SERVER],
        [8, "sudo sed -i -e 's/Server=127.0.0.1/Server=%s/g' /usr/local/zabbix/conf/zabbix_agentd.conf"
         % ZABBIX_SERVER],
        [9, "sudo sed -i -e 's/Hostname=Zabbix\ server/Hostname=%s/g' /usr/local/zabbix/conf/zabbix_agentd.conf"
         % name],
        [3, 'sudo useradd zabbix'],
        [12, 'sudo /usr/local/zabbix/sbin/zabbix_agentd -c /usr/local/zabbix/conf/zabbix_agentd.conf']
    ]

    return tasks


def task(host):
    tasks = general_task(host[0])
    session = connect(host[1])
    if session:
        for command in tasks:
            stdin, stdout, stderr, status = session.call(command[1])
            if status != 0 and command[0] < 4:
                print 'Host: %s, Failed Command: %s' % (host, command[1])
            elif status != 0 and command[0] >= 4:
                print 'Host: %s, Failed Command: %s' % (host, command[1])
                session.close()
            else:
                print '%s execute %s success' % (host, command[1])
        print host[0], host[1], '|'


class ThreadTask(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            host = self.queue.get()
            try:
                print 'Task of %s Start.' % host
                task(host)
            except Exception, e:
                print 'Task of %s Failed: %s' % (host, e)
            self.queue.task_done()


def install():
    for i in range(THREAD_NUM):
        t = ThreadTask(QUEUE)
        t.setDaemon(True)
        t.start()

    for host in HOSTS:
        QUEUE.put(host)
    QUEUE.join()

if __name__ == '__main__':
    install()
