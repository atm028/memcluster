#The class implements the main inteface of the cluster.
#It's initiate connections to the set of primary and buckup nodes.
#The class provides interface to put hte record into the cluster,
#read it and delete.

#During initialization it start monitoring services for each of
#primary servers. If the server stops answering on ping then we
#thing that it doesn't available anymore and we have to remove
#server from list of primary servers of Consistent Hash. If the
#node still is in configuration file then this server will not
#be removed from the list of servers and monitoring service
#still trying to ping the server. If target server start
#answering on the ping then the server will be added into
#the hash tabe of the Consisten Hash class.

import chush
from probe import ServiceMonitor as MemcacheClusterMonitor
import memcache


def nodeStateCallback(state, address):
	return True


class memcluster():
	def __init__(self, prim_nodes=[], bckp_nodes=[]):
		self.prim_nodes = prim_nodes
		self.bckp_nodes = bckp_nodes
		self._conn = {}
		self._init = False

		# will use same hush for prim and backup based on prim nodes
		self.hush = chush.ConsistentHash(self.prim_nodes)

		MemcacheClusterMonitor(nodeStateCallback, prim_nodes, 5, self).start()

		for i in range(0, len(self.prim_nodes)):
			self._conn[self.prim_nodes[i]] = [memcache.Client([self.prim_nodes[i]]),
				memcache.Client([self.bckp_nodes[i]])]

		self._init = True

	def isInit(self):
		return self._init

	def set(self, key, data):
		addr = self.hush.getServer(key)

		return self.setbyAddr(addr, key, data)

	def get(self, key):
		addr = self.hush.getServer(key)

		return self.getByAddr(addr, key)

	def setbyAddr(self, addr, key, data):
		res = []

		res.append(self._conn[addr][0].set(key, data))
		res.append(self._conn[addr][1].set(key, data))

		return res

	def getByAddr(self, addr, key):
		res = None
		res = self._conn[addr][0].get(key)
		if res is not None:
			return res

		res = self._conn[addr][1].get(key)
		if res is not None:
			return res

		return None

	def delete(self, addr, key):
		return True
