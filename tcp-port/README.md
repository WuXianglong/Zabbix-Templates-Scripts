Template for Discovery Port
===========================

Check TCP port status in Zabbix using discovery.

INSTALL
-------

### Add User Parameters

Copy get_port.py to /usr/local/zabbix/bin/ and run "sudo chmod 777 get_port.py"
Copy tcp-port.conf to /usr/local/zabbix/conf/zabbix_agentd/. Restart Zabbix agent.
Add line "Include=/usr/local/zabbix/conf/zabbix_agentd/*.conf" in /usr/local/zabbix/conf/zabbix_agentd.conf

### Add discovery

See: http://www.linuxyan.com/cacti-nagios/396.html

