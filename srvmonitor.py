import os
import threading
import re
import time

__timeToLeave = 0


class LocalServiceMonitor(threading.Thread):
	def __init__(self, srv_log_file, interval=5, callback=None):
		threading.Thread.__init__(self)

		self.srv_log_file = srv_log_file
		self.last_time = os.stat(self.srv_log_file).st_mtime
		self.interval = interval
		self.offset = 0
		self.cbk = callback

	def leave(self):
		__timeToLeave = 1

	def checkIfChanged(self):
		self.this_time = os.stat(self.srv_log_file).st_mtime
		if self.this_time > self.last_time:
			self.last_time = self.this_time
			return True
		return False

	def checkState(self):
		state_line = ""

		file = open(self.srv_log_file, "r")
		file.seek(self.offset)

		lines = file.readlines()

		self.offset = file.tell()

		file.close()

		for i in _lines:
			if (re.search("notice: running", i)) or (re.search("notice: exiting", i)):
				state_line = i

		self.curr_state = state_line.split("general: notice: ")[1]

	def run(self):
		self.checkState()

		while not __timeToLeave:
			if self.checkIfChanged():
				checkState()
				if self.cbk is not None:
					self.cbk(self.curr_state)

			time.sleep(self.interval)
