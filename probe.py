#Description:
# Class ServiceMonitor is module for monitoring memcahced cluster nodes.
# If some of node stop answer then callback with address of non-answered
# node will be called.

import threading
import time
import memcache

__timeToLeave = 0


class ServiceMonitor(threading.Thread):
	def __init__(self, callback, nodes, interval, connector):
		threading.Thread.__init__(self)

		self._nodes = nodes
		self._cbk_func = callback
		self._interval = interval
		self._connector = connector
		self._state = []

		for i in range(0, len(self._nodes)):
			self._state.append(True)

	def leave(self):
		__timeToLeave = 1

	def addServer(self, node):
		self._nodes.append(node)

	def removeServer(self, node):
		self._nodes.remove(node)

	def probe(self, addr):
		if self._connector.isInit() is True:
			res = self._connector.setbyAddr(addr, addr + "_key", addr + "_data")
			return res[0] and res[1]

		self._connector.delete(addr, addr + "_key")

		return True

	def run(self):
		while not __timeToLeave:
			for addr in self._nodes:
				if self.probe(addr) is True and
				self._state[self._nodes.index(addr)] is False:
					self._cbk_func(True, addr)
					self._state[self._nodes.index(addr)] is True

				if self.probe(addr) is False and
				self._state[self._nodes.index(addr)] is True:
					self._cbk_func(False, addr)
					self._state[self._nodes.index(addr)] = False

			time.sleep(self._interval)
