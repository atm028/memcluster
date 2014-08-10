from binascii import crc32
from netaddr import IPAddress


class ConsistentHash():
	def __init__(self, server_list=[]):
		self.server_points = []

		for addr in server_list:
			self.addServer(addr)

	def addServer(self, server):
		ip = server.split(":")
		self.server_points.append([crc32(str(ip[0])) & 0xffffffff,
			int(IPAddress(ip[0])), int(ip[1])])

	def removeServer(self, server):
		ip = server.split(":")
		self.server_points.remove([crc32(str(ip[0])) & 0xffffffff,
			int(IPAddress(ip[0])), int(ip[1])])

	def getServer(self, key):
		hash = crc32(key) & 0xffffffff
		diff = 0xffffffff
		ind = 0

		for rec in self.server_points:
			tdiff = abs(rec[0] - hash)
			if tdiff < diff:
				diff = tdiff
				ind = self.server_points.index(rec)

		return str(IPAddress(self.server_points[ind][1])) +
		":" + str(self.server_points[ind][2])
