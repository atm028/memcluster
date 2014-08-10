import memcluster

import threading
import time
import socket
import subprocess
import re

# There are should be three distributed tables.
# The second table contains the status of each GTM server.
# The third table contanins status of each DNS server.

# All tables described by the record structure:
# addr - the IP address of the server
# name - host name. should be providet by the node.
# status - current status of server.
# schd - if the unavailable status is planned. This status should be
#		marked by the node which plan to become unavailable.
# ping_time - the timeof ping to the application
# old_srv - the address of the server which has been recorded before.
#		If it is the first record then this field will be empyt
# curr_srv - the address of server which placed the current value of
#		the ping time
# type - descirbes the type of the record
#	0 - None
#	1 - Application
#	2 - GTM
#	3 - DNS
#	>3 - Is not applicable


class ServiceType():
	NO_SRV = 0
	APPL_SRV = 1
	GTM_SRV = 2
	DNS_SRV = 3


class MCRecord():
	addr = None
	name = None
	status = None
	schd = None
	ping_time = None
	old_srv = None
	curr_srv = None
	srv_type = 0

	def __init__(self, addr, name, status, schd, ping_time,
		old_srv, curr_srv, srv_type):

		self.addr = addr
		self.name = name
		self.status = status
		self.schd = schd
		self.ping_time = ping_time
		self.old_srv = old_srv
		self.curr_srv = curr_srv
		self.srv_type = srv_type


# The service has to serve:
# - application
# - DNS services
# - GTM services

# When it going to start:
# - read CME
# - get the list of DNS servers
# - get the list of GTM services
# - start thread for ping DNS
# 	- Put the record with description of itself
# 	- then strat ping of all DNS servers in the loop
# - start thread for ping GTM
# 	- Put the record with description of itself
# 	- then strat ping of all GTM servers in the loop

# Define class of pinging service
__timeToLeave = 0
optionScheduledReboot = False


class ServicePing(threading.Thread):
	def __init__(self, srv_name, srv_list, dcash,
		srv_type=ServiceType.NO_SRV, interval=10):
		threading.Thread.__init__(self)

		self.srv_name = srv_name
		self.srv_list = srv_list
		self.dcash = dcash
		self.srv_type = srv_type
		self.interval = interval

	def leave(self):
		__timeToLeave = 1

	def ping(self, addr):
		key = self.srv_name + "_" + addr
		info = self.dcash.get(key)

		if info is None:
			curr_srv = self.srv_name
		else:
			curr_srv = info.curr_srv

		res = subprocess.Popen(["ping", "-W", "50", "-c", "1", addr],
			stdout=subprocess.PIPE).communicate()[0]
		res = re.search("time=(\d+.\d+)", res)

		data = None
		if res is not None:
			if self.srv_name == info.curr_srv or
			float(res.groups()[0]) < float(info.ping_time):
				data = MCRecord(addr, key, True, False, res.groups()[0],
					curr_srv, socket.gethostname(), ServiceType.DNS_SRV)
		else:
			data = MCRecord(addr, key, False, False, 255,
				curr_srv, socket.gethostname(), ServiceType.DNS_SRV)

		if data is not None:
			self.dcash.set(key, data)

	def run(self):
		while not __timeToLeave:
			for addr in self.srv_list:
				self.ping(addr)

			time.sleep(self.interval)


# memcached cluster
prim_srv = ["54.215.149.227:8080", "54.215.135.42:8080"]
bckp_srv = ["54.215.135.42:8090", "54.215.149.227:8090"]
mc = memcluster.memcluster(prim_srv, bckp_srv)

dns_servers = ["192.168.73.185", "192.168.73.240", "192.168.73.237"]
ServicePing("DNS", dns_servers, mc, ServiceType.DNS_SRV).start()
ServicePing("GTM", dns_servers, mc, ServiceType.DNS_SRV).start()
