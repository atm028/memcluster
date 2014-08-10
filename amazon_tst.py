import memcluster as mc
import threading


class setThread(threading.Thread):
	def __init__(self, threadID, name, r1, r2):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.r1 = r1
		self.r2 = r2

	def run(self):
		print self.name + " thread started"

		for i in range(self.r1, self.r2):
			print "SIP_Cluster_appl_" + str(i)
			mc.mc.set("SIP_Cluster_appl_" + str(i), i)

		print self.name + " thread stopped"


threads = []
r1 = 0
r2 = 0

for i in range(1, 3):
	r1 = r2 + 1
	r2 += 10
	threads.append(setThread(i, "Thread_" + str(i), r1, r2))


for i in range(0, 2):
	threads[i].start()
