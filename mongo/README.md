Template Mongo
==============

Show Mongo status in Zabbix.

INSTALL
-------

Assume the Zabbix agent is installed in /zabbix-agent/ directory.

### Add User Parameters

Add line "Include=/usr/local/zabbix/conf/zabbix_agentd/*.conf" in /usr/local/zabbix/conf/zabbix_agentd.conf
Copy mongo.conf to /usr/local/zabbix/conf/zabbix_agentd/. Restart Zabbix agent.

### Import Template

Import mongodb-template.xml, and link it to a host.

